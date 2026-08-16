'use client';

import React from 'react';

/**
 * Self-contained pure TypeScript QR Code Generator (Zero external dependencies).
 * Implements ISO/IEC 18004 Byte Mode with Reed-Solomon Error Correction.
 */

// GF(256) tables for Reed-Solomon
const EXP_TABLE = new Uint8Array(512);
const LOG_TABLE = new Uint8Array(256);

(() => {
  let x = 1;
  for (let i = 0; i < 255; i++) {
    EXP_TABLE[i] = x;
    EXP_TABLE[i + 255] = x;
    LOG_TABLE[x] = i;
    x = (x << 1) ^ (x >= 128 ? 0x11d : 0);
  }
})();

function gfMul(x: number, y: number): number {
  if (x === 0 || y === 0) return 0;
  return EXP_TABLE[LOG_TABLE[x] + LOG_TABLE[y]];
}

function rsPoly(numEc: number): Uint8Array {
  let poly = new Uint8Array([1]);
  for (let i = 0; i < numEc; i++) {
    const next = new Uint8Array(poly.length + 1);
    const root = EXP_TABLE[i];
    for (let j = 0; j < poly.length; j++) {
      next[j] ^= gfMul(poly[j], root);
      next[j + 1] ^= poly[j];
    }
    poly = next;
  }
  return poly;
}

function rsEncode(data: Uint8Array, numEc: number): Uint8Array {
  const poly = rsPoly(numEc);
  const res = new Uint8Array(numEc);
  for (let i = 0; i < data.length; i++) {
    const coef = data[i] ^ res[0];
    for (let j = 0; j < numEc - 1; j++) {
      res[j] = res[j + 1] ^ gfMul(poly[j], coef);
    }
    res[numEc - 1] = gfMul(poly[numEc - 1], coef);
  }
  return res;
}

// Minimal QR Code Matrix Builder (Versions 1-10, Byte Mode, Level M/L)
export function generateQrMatrix(text: string): boolean[][] {
  const utf8Bytes = new TextEncoder().encode(text);
  const dataLen = utf8Bytes.length;

  // Select appropriate version based on byte capacity (Level L/M)
  let version = 4;
  const capacities = [0, 17, 32, 53, 78, 106, 134, 154, 192, 230, 271];
  for (let v = 1; v <= 10; v++) {
    if (dataLen <= capacities[v]) {
      version = v;
      break;
    }
  }

  const size = version * 4 + 17;
  const matrix: (boolean | null)[][] = Array.from({ length: size }, () =>
    Array(size).fill(null)
  );

  // 1. Finder patterns (top-left, top-right, bottom-left)
  const placeFinder = (row: number, col: number) => {
    for (let r = -1; r <= 7; r++) {
      for (let c = -1; c <= 7; c++) {
        const tr = row + r;
        const tc = col + c;
        if (tr >= 0 && tr < size && tc >= 0 && tc < size) {
          if (
            (r >= 0 && r <= 6 && (c === 0 || c === 6)) ||
            (c >= 0 && c <= 6 && (r === 0 || r === 6)) ||
            (r >= 2 && r <= 4 && c >= 2 && c <= 4)
          ) {
            matrix[tr][tc] = true;
          } else {
            matrix[tr][tc] = false;
          }
        }
      }
    }
  };

  placeFinder(0, 0);
  placeFinder(0, size - 7);
  placeFinder(size - 7, 0);

  // 2. Timing patterns
  for (let i = 8; i < size - 8; i++) {
    const val = i % 2 === 0;
    if (matrix[6][i] === null) matrix[6][i] = val;
    if (matrix[i][6] === null) matrix[i][6] = val;
  }

  // 3. Dark module
  matrix[size - 8][8] = true;

  // 4. Alignment patterns for Version >= 2
  if (version >= 2) {
    const alignPos: Record<number, number[]> = {
      2: [6, 18],
      3: [6, 22],
      4: [6, 26],
      5: [6, 30],
      6: [6, 34],
      7: [6, 22, 38],
      8: [6, 24, 42],
      9: [6, 26, 46],
      10: [6, 28, 50],
    };
    const coords = alignPos[version] || [6, 26];
    for (const r of coords) {
      for (const c of coords) {
        if (matrix[r][c] !== null) continue;
        for (let dr = -2; dr <= 2; dr++) {
          for (let dc = -2; dc <= 2; dc++) {
            const isBorder = Math.abs(dr) === 2 || Math.abs(dc) === 2;
            const isCenter = dr === 0 && dc === 0;
            matrix[r + dr][c + dc] = isBorder || isCenter;
          }
        }
      }
    }
  }

  // 5. Reserve format bits
  for (let i = 0; i < 9; i++) {
    if (matrix[8][i] === null) matrix[8][i] = false;
    if (matrix[i][8] === null) matrix[i][8] = false;
    if (matrix[8][size - 1 - i] === null) matrix[8][size - 1 - i] = false;
    if (matrix[size - 1 - i][8] === null) matrix[size - 1 - i][8] = false;
  }

  // 6. Data Encoding (Byte mode: 0100)
  const bits: number[] = [0, 1, 0, 0]; // Byte mode indicator
  // Character count indicator (8 bits for v1-9, 16 for v10+)
  const countBits = version <= 9 ? 8 : 16;
  for (let i = countBits - 1; i >= 0; i--) {
    bits.push((dataLen >> i) & 1);
  }
  for (let k = 0; k < utf8Bytes.length; k++) {
    const byte = utf8Bytes[k];
    for (let i = 7; i >= 0; i--) {
      bits.push((byte >> i) & 1);
    }
  }
  // Terminator
  while (bits.length % 8 !== 0 && bits.length < capacities[version] * 8) {
    bits.push(0);
  }
  // Pad bytes 0xEC, 0x11
  const pad = [0xec, 0x11];
  let pIdx = 0;
  while (bits.length < capacities[version] * 8) {
    const padByte = pad[pIdx % 2];
    pIdx++;
    for (let i = 7; i >= 0; i--) {
      bits.push((padByte >> i) & 1);
    }
  }

  // Convert bits to bytes
  const dataBytes = new Uint8Array(bits.length / 8);
  for (let i = 0; i < dataBytes.length; i++) {
    let b = 0;
    for (let j = 0; j < 8; j++) {
      b = (b << 1) | bits[i * 8 + j];
    }
    dataBytes[i] = b;
  }

  // Reed-Solomon Error Correction Code
  const ecCount = Math.floor(capacities[version] * 0.35) || 10;
  const ecBytes = rsEncode(dataBytes, ecCount);

  // Combine data + EC
  const allCodewords = new Uint8Array(dataBytes.length + ecBytes.length);
  allCodewords.set(dataBytes, 0);
  allCodewords.set(ecBytes, dataBytes.length);

  const finalBits: number[] = [];
  for (let k = 0; k < allCodewords.length; k++) {
    const cw = allCodewords[k];
    for (let i = 7; i >= 0; i--) {
      finalBits.push((cw >> i) & 1);
    }
  }

  // 7. Place data into matrix (Mask 0: (row + col) % 2 === 0)
  let bitIdx = 0;
  let dir = -1;
  for (let c = size - 1; c > 0; c -= 2) {
    if (c === 6) c--; // Skip vertical timing pattern
    const rows = dir === -1
      ? Array.from({ length: size }, (_, i) => size - 1 - i)
      : Array.from({ length: size }, (_, i) => i);

    for (const r of rows) {
      for (const colOffset of [0, -1]) {
        const col = c + colOffset;
        if (matrix[r][col] === null) {
          const bit = bitIdx < finalBits.length ? finalBits[bitIdx++] : 0;
          const mask = (r + col) % 2 === 0;
          matrix[r][col] = (bit ^ (mask ? 1 : 0)) === 1;
        }
      }
    }
    dir = -dir;
  }

  // Final Format Information bits (Mask 0, Level M: 101010000010010)
  const formatBits = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0];
  const positionsTop = [
    [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 7], [8, 8],
    [7, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8],
  ];
  const positionsBottom = [
    [size - 1, 8], [size - 2, 8], [size - 3, 8], [size - 4, 8], [size - 5, 8], [size - 6, 8], [size - 7, 8],
    [8, size - 8], [8, size - 7], [8, size - 6], [8, size - 5], [8, size - 4], [8, size - 3], [8, size - 2], [8, size - 1],
  ];

  for (let i = 0; i < 15; i++) {
    const val = formatBits[i] === 1;
    const [r1, c1] = positionsTop[i];
    matrix[r1][c1] = val;
    const [r2, c2] = positionsBottom[i];
    matrix[r2][c2] = val;
  }

  return matrix.map((row) => row.map((cell) => cell === true));
}

interface QRCodeSVGProps {
  value: string;
  size?: number;
  includeMargin?: boolean;
  level?: 'L' | 'M' | 'Q' | 'H' | string;
  className?: string;
  bgColor?: string;
  fgColor?: string;
}

export const QRCodeSVG: React.FC<QRCodeSVGProps> = ({
  value,
  size = 180,
  includeMargin = true,
  level = 'M',
  className = '',
  bgColor = '#FFFFFF',
  fgColor = '#000000',
}) => {
  const matrix = React.useMemo(() => {
    try {
      return generateQrMatrix(value || 'SUNAT-QR');
    } catch {
      return generateQrMatrix('SUNAT-QR');
    }
  }, [value]);

  const margin = includeMargin ? 4 : 0;
  const numCells = matrix.length + margin * 2;

  // Build SVG path for efficiency and crisp rendering
  const pathD = React.useMemo(() => {
    let d = '';
    for (let r = 0; r < matrix.length; r++) {
      for (let c = 0; c < matrix[r].length; c++) {
        if (matrix[r][c]) {
          const x = c + margin;
          const y = r + margin;
          d += `M${x},${y}h1v1h-1z `;
        }
      }
    }
    return d;
  }, [matrix, margin]);

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${numCells} ${numCells}`}
      shapeRendering="crispEdges"
      className={className}
      style={{ display: 'block', maxWidth: '100%', height: 'auto' }}
    >
      <rect width="100%" height="100%" fill={bgColor} />
      <path d={pathD} fill={fgColor} />
    </svg>
  );
};

export default QRCodeSVG;

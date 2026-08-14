/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'http://backend:8000/api/v1/:path*'
      }
    ]
  }
};

module.exports = nextConfig;

import React from 'react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-12">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Branding */}
          <div>
            <h3 className="text-lg font-bold text-[#00A9E0] mb-2">FINIA</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Sinergia Operativa y Negociación Inteligente con IA - Movistar Empresas
            </p>
          </div>

          {/* Documentation */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Documentación</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  API Docs
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Guía de Usuario
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  FAQ
                </a>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Soporte</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>
                <a href="mailto:support@finia.local" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Email Support
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Centro de Ayuda
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Estado del Servicio
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Privacidad
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Términos de Servicio
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                  Cookie Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 dark:border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {currentYear} FINIA. Todos los derechos reservados.
            </p>
            <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
              <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                Twitter
              </a>
              <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                LinkedIn
              </a>
              <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

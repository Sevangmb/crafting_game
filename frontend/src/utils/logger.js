/**
 * Système de logging conditionnel
 * Les logs ne s'affichent qu'en mode développement
 */

const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
    /**
     * Log d'information (uniquement en développement)
     */
    log: (...args) => {
        if (isDevelopment) {
            console.log(...args);
        }
    },

    /**
     * Log d'information détaillée (uniquement en développement)
     */
    info: (...args) => {
        if (isDevelopment) {
            console.info(...args);
        }
    },

    /**
     * Log d'avertissement (toujours affiché)
     */
    warn: (...args) => {
        console.warn(...args);
    },

    /**
     * Log d'erreur (toujours affiché)
     */
    error: (...args) => {
        console.error(...args);
    },

    /**
     * Log de debug avec contexte (uniquement en développement)
     */
    debug: (context, ...args) => {
        if (isDevelopment) {
            console.log(`[${context}]`, ...args);
        }
    },

    /**
     * Log de groupe (uniquement en développement)
     */
    group: (label, callback) => {
        if (isDevelopment) {
            console.group(label);
            callback();
            console.groupEnd();
        }
    }
};

export default logger;

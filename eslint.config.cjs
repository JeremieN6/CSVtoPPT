// ESLint flat config
const vueParser = require('vue-eslint-parser');
const espree = require('espree');

module.exports = [
  {
    ignores: [
      'dist/**',
      'backend/static/**',
      'node_modules/**',
    ],
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: espree,
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
  },
  {
    files: ['**/*.{js,mjs,cjs}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
  },
];

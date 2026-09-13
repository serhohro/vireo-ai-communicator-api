/** @type {import('jest').Config} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  testPathIgnorePatterns: [
    '/node_modules/',
    'tests/integration.test.ts',  // TODO: v3.3.1 — адаптувати під v3.1 wire format
  ],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        target: 'ES2020',
        module: 'CommonJS',
        esModuleInterop: true,
        strict: false,
        skipLibCheck: true,
        resolveJsonModule: true,
        isolatedModules: true,
      },
    }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
};

const ACCESS_SECRET_KEY = "JWT_ACCESS_SECRET";
const REFRESH_SECRET_KEY = "JWT_REFRESH_SECRET";

function getRequiredEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

export const env = {
  jwtAccessSecret: getRequiredEnv(ACCESS_SECRET_KEY),
  jwtRefreshSecret: getRequiredEnv(REFRESH_SECRET_KEY),
};

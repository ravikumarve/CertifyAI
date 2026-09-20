import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow dev HMR + fonts when the dev server is opened via 127.0.0.1
  // (default is localhost-only; without this the dev client reload-loops).
  allowedDevOrigins: ["127.0.0.1"],
};

export default nextConfig;

import data from './data.json' assert { type: 'json' }

export default async (req, context) => {
  const { path1 } = context.params;

  console.log(data)

  return new Response(`You're visiting ${path1}!`);
};

export const config = {
  path: "/api/v0/:path1"
};
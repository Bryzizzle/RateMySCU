// const data = {
//
// }

export default async (req, context) => {
  const { path1 } = context.params;

  return new Response(`You're visiting ${path1}!`);
};

export const config = {
  path: "/api/v0/:path1"
};
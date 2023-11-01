// const data = {
//
// }

export default async (req, context) => {
  const { path1, path2 } = context.params;

  return new Response(`You're visiting ${path1} and ${path2}!`);
};

export const config = {
  path: "/api/v0/:path1/:path2"
};
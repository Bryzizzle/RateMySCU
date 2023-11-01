export default async (req, context) => {
  const { path1, path2, path3 } = context.params;

  return new Response(`You're visiting ${path1}, ${path2}, and ${path3}!`);
};

export const config = {
  path: "/api/v0/:path1/:path2/:path3"
};
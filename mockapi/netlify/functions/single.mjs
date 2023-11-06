import data from './data.json'

export default async (req, context) => {
    const { path1 } = context.params;

    return new Response(data["data"][path1]);
};

export const config = {
    path: "/api/v0/:path1"
};
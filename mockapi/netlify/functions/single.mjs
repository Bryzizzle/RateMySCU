import data from './data.json'

export default async (req, context) => {
    const { path1 } = context.params;

    const resp = data["data"][path1];
    console.log(resp);

    return Response.json(resp);
};

export const config = {
    path: "/api/v0/:path1"
};
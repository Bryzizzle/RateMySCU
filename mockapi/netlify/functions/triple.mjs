import data from './data.json'

export default async (req, context) => {
    const { path1, path2, path3 } = context.params;

    // Retrieve the associated response
    const path = `${path1}/${path2}/${path3}`
    let resp = data.data[path];

    // If the request is not defined in the data.json file, then return a 404 response
    if (resp === undefined) {
        resp = data._notfound
    }

    return Response.json(resp.response, {status: resp.status_code});
};

export const config = {
    path: "/api/v0/:path1/:path2/:path3"
};
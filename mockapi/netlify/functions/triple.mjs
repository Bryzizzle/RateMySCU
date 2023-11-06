import data from './data.json'

export default async (req, context) => {
    const { path1, path2, path3 } = context.params;
    let resp;

    // Retrieve the associated response, if it fails then set it to undefined
    try {
        resp = data.data[path1][path2][path3];
    } catch (e) {
        resp = undefined;
    }

    // If the request is not defined in the data.json file, then return a 404 response
    if (resp === undefined) {
        resp = data._notfound
    }

    return Response.json(resp.response, {status: resp.status_code});
};

export const config = {
    path: "/api/v0/:path1/:path2/:path3"
};
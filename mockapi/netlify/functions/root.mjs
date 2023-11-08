import data from './data.json'

export default async (req, context) => {
    const { path } = context.params;

    if (path === "check"){
        return Response.json({"status": "OK", "version": "dev"}, {status: 200});
    }

    return Response.redirect("https://ratemyscu.bryan.cf", 307);
};

export const config = {
    path: "/:path"
};
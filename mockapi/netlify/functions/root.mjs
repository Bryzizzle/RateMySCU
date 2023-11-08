import data from './data.json'

export default async (req, context) => {
    return Response.redirect("https://ratemyscu.bryan.cf", 307)
};

export const config = {
    path: "/:path"
};
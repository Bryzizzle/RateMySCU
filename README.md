# RateMySCU
For SCU students who would like to quickly compare professors and classes, **RateMySCU** is an application that allows students to painlessly summarize information about a particular class and professor quickly. Unlike CourseEval RateMySCU allows students to view information spread across multiple sources without downloading numerous PDFs.

## Infrastructure
This project consists of four distinct services as listed below:

| Service Name                                                      | Description                                                                                                                                        | Hosting Provider | Deploy Status                                                                                                                                                             |
|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Frontend](https://ratemyscu.bryan.cf) [(src)](./frontend)        | Main user-facing application that users interact with.                                                                                             | Netlify          | [![Netlify Status](https://api.netlify.com/api/v1/badges/fe374963-a870-4412-a177-f1c457f6ca1d/deploy-status)](https://app.netlify.com/sites/ratemyscu/deploys)            |
| [Backend](https://backend.ratemyscu.bryan.cf) [(src)](./backend)  | A REST API used by the front-end service to retrieve course evaluation data. It also handles PDF processing and data storage.                      | Vercel           | ![Backend Status](https://therealsujitk-vercel-badge.vercel.app/?app=ratemyscu)                                                                                           |
| [Static](https://static.ratemyscu.bryan.cf) [(src)](./static)     | Hosts static files (such as images) that will be used by multiple services.                                                                        | Netlify          | [![Static Host Status](https://api.netlify.com/api/v1/badges/725b4dae-90a0-4e17-bd4e-bb60c6a9f309/deploy-status)](https://app.netlify.com/sites/static-ratemyscu/deploys) |
| [Mock API](https://mockapi.ratemyscu.bryan.cf) [(src)](./mockapi) | A Mock Backend endpoint that returns a predefined value. This allows for development of the frontend service in parallel with the backend service. | Netlify          | [![Backend Status](https://api.netlify.com/api/v1/badges/2408b928-fc17-40c1-9144-af5aaf8cee45/deploy-status)](https://app.netlify.com/sites/mockapi-ratemyscu/deploys)    |
| [Status Page](https://status.ratemyscu.bryan.cf)                  | Monitors the uptime and availability of each of the services above.                                                                                | HetrixTools      |                                                                                                                                                                           |

Please note that the root path of each service above **automatically redirects you** to the user-facing
frontend site. As such, it will seem like all the services above point to one page.

More detail about each service can be viewed by following the `(src)` link on the table.
This will bring you to the respective source folder for each service which contains a more detailed
README file on that service.
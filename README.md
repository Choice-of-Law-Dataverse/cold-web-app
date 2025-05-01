# CoLD Web App
Repository for building and deploying the CoLD web app on [www.cold.global](https://www.cold.global/).

## API Documentation
The API documentation can be found [here](https://cold-container-test.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/api/v1/docs).

## Versioning and Deployment Policy
We continuously deploy the backend and frontend independently of each other. Each component evolves at its own pace, with versioning applied as changes are introduced.

When creating a new "official" release of the repository, we align the version numbers of the backend and frontend to the highest version number between the two, ensuring consistency. This may involve incrementing the version of the component that is "lagging behind" to match the other.

This approach allows for flexibility in development while maintaining coherence in official releases.

## Language Style Guide
For website and data input
- Language: `en-US` – English as used in the United States
- Apply "Bluebook" title case style for titles, convert titles [here](https://titlecaseconverter.com/)
- When in doubt, look to [George](https://en.wikipedia.org/wiki/Politics_and_the_English_Language#Remedy_of_Six_Rules)

## Running the web app on your local machine
- Open Terminal
- Navigate to `cold-web-app/frontend`: Type in `cd` and drag-and-drop the `frontend` folder into terminal, then hit `Enter`
- Run `npm run dev`
- Open http://localhost:3000/ in a browser

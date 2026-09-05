# Changelog

## [1.1.1](https://github.com/Choice-of-Law-Dataverse/cold-web-app/compare/backend-v1.1.0...backend-v1.1.1) (2026-09-05)


### Bug Fixes

* support NocoDB 2026.08.2 upgrade ([#538](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/538)) ([12c1fb3](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/12c1fb3c6c897f996343f63ce4e7bf99e10036c1)), closes [#537](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/537)

## [1.1.0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/compare/backend-v1.0.0...backend-v1.1.0) (2026-08-23)


### Features

* move technical wiki into main site ([#535](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/535)) ([e803de4](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/e803de4123c03206dd1ae5d8fe9ee519a4a5888d))

## [1.0.0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/compare/backend-v0.2.16...backend-v1.0.0) (2026-08-23)


### Features

* add cross-compatible agent instructions for CoLD web application development ([#225](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/225)) ([615f05e](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/615f05ed7c02cd1117df11dbbb29e1bf5c340c2b))
* add email notifications for new suggestions ([#400](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/400)) ([ef70016](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/ef70016cf4d90b03d7503620b20c6139658966be))
* add entity relations generator and HCCH answer drawer ([#447](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/447)) ([4ff9e4b](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/4ff9e4bc403dc3223d070e54d4cae93fd3b5397d))
* add heartbeats for streaming endpoints ([#393](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/393)) ([e45a7ed](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/e45a7edc9c39afa82e0b9d946d9aa5cedc584542))
* add PR workflow with path-filtered checks ([#355](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/355)) ([99a3c66](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/99a3c66b2d16f8afe27ba88a912f4faf273ae36d))
* **api:** add GET alternatives to data fetching endpoints ([#495](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/495)) ([75ce7d5](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/75ce7d53467202fc5aa6329972c11609e15d16a3))
* automate case_analyzer suggestion insertion into Court_Decisions table ([#337](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/337)) ([fbcb7ea](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/fbcb7eae7594116f837e6efb66ffee6fd9037484))
* basic logfire instrumentation ([#328](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/328)) ([e4222be](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/e4222be6d8c1d8f286a24530fc272e03cda6a561))
* **case-analyzer:** add response chaining, guardrails, and retry ([#438](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/438)) ([10fcced](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/10fccedc2b9dde1a877d016ca67266154f845417))
* **court-decision:** leading cases page + jurisdiction pill fixes ([#474](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/474)) ([0a1bbf2](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/0a1bbf23c698d05ff881d3e60d00d8dfb39b342c))
* **entities:** slim list API + shared frontend components ([#506](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/506)) ([0f39759](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/0f39759d4db1b803000f66108316adc92379e23f))
* entity feedback ([#399](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/399)) ([32fc880](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/32fc880e29f3c374c71b694ea46e15c585e0ef03))
* implement connection pooling and singleton managers for database and HTTP connections ([#307](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/307)) ([fb83960](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/fb839603dd2417827387e19341cbd827c5463b4e))
* implement draft recovery and moderation enhancements ([#373](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/373)) ([469c72b](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/469c72bc3ab60c25d12499e04ca94191621c8b78))
* integrate AI case analysis workflow from cold-case-analysis with Azure Storage ([#367](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/367)) ([71bc9c9](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/71bc9c9edf20e06fa04b725f417b3827d111f02e))
* integrate Auth0 for backend and frontend authentication ([#343](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/343)) ([281dfd0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/281dfd08b40977f02407bc9e64b64fcc00999394))
* **moderation:** redesign dashboard, BibTeX citations, and security hardening ([#459](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/459)) ([b80f5a9](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/b80f5a911e75ff46f4adaf6504b025488bfe6420))
* move moderation features from backend HTML to frontend with proper API endpoints ([#345](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/345)) ([a101b47](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/a101b47944d644f32437d5d668a56f2981acd741))
* refactor mapping configurations from JSON to Python classes with enum support ([#357](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/357)) ([597643d](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/597643d05e62bea6a60a92ca8e5d5b163f40cc05))
* **region-filter:** fix region filtering and move tabs to dropdown ([#444](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/444)) ([4a66d09](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/4a66d098d1edf79b2d0b30fa12ade8d540845f7a))
* replace static jurisdiction counts JSON with dynamic API endpoint ([#303](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/303)) ([1efa4b6](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/1efa4b65e4d451ffef997bface42692f3ea8140b))
* **search:** add arbitral awards and arbitral rules to full-text search ([#427](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/427)) ([8ed8370](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/8ed8370fde4b4acda4751038f91c36b2fbaf128f))
* **search:** return curated search results with proper typing ([#455](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/455)) ([6abfb2d](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/6abfb2defca54ecb72bfd77bac691b517d14ddb9))
* show answer coverage in map ([#308](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/308)) ([d9443a0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/d9443a0e117734d5d35a251e1969fc7df88b757c))
* **specialist:** add specialists listing page ([#487](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/487)) ([bfd6ed7](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/bfd6ed7645fbc2ebce1dabab8eb39a96f12a36fc))
* use NocoDB API for case analyzer court decisions with Azure blob PDF uploads ([#340](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/340)) ([239551a](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/239551aef2bfebd0ed558a856d96a489baa40119))
* **views:** derive question relations through answers in get_entity_detail ([#511](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/511)) ([6f3d8af](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/6f3d8af5e64ac77305ca80a7f0bb500828d78c6d))


### Bug Fixes

* **case-analyzer:** eliminate output pollution and upgrade to GPT-5.4 ([#458](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/458)) ([035af23](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/035af2346736c5d8f392a97c95095b7281cb3574))
* **ci:** unblock frontend deploy and stop leaking Auth0 secrets into the public image ([#526](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/526)) ([508c0fd](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/508c0fd2612f5b2c2222cb39f08d7c54154bf258))
* **frontend:** resolve nuxt prepare crash and drawer header polish ([#517](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/517)) ([455b7e0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/455b7e0314d3172b610a342565a894f7b179ec73))
* query specialists for jurisdictions ([#327](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/327)) ([1197269](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/1197269e7a5f8c42388cdf56b73bc735970924fc))
* remove external IP service calls for privacy compliance ([#233](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/233)) ([ae3507f](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/ae3507f3c6c164bb5db551209da9c1589cb03e26))
* render pages server-side and rebuild the SEO surface ([#529](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/529)) ([8ed31e1](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/8ed31e15ba14ed7356b534a90b7ea3d5a61a7f7f))
* **search:** correct answer filtering to use cold_id ([#429](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/429)) ([5c508a6](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/5c508a68bbd4c6beba1f4c3ded0ab901ea0ac08d))
* sort chronological relations newest-first in get_entity_detail ([#472](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/472)) ([7aa8855](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/7aa885590655bdded8fb11da768938ef7fc23a18))
* standardize casing for "Jurisdictions Alpha-3 Code" in mapping and tests ([#378](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/378)) ([d2e9ba0](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/d2e9ba008c6c49fd7cf95c913ebd08e180dbd9d0))
* **views:** add _sortable_date(date) overload so arbitral-institution detail loads ([#493](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/493)) ([2c095ce](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/2c095cee35e9223a8365eedca9f45df32ecdc92f))
* **views:** dedupe Question text in data_views.answers search rows ([#512](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/512)) ([cb9cf1a](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/cb9cf1a4b7b40a71ffd2f19f164d9b6a9cabd935))


### Performance Improvements

* **homepage:** paginate full_table and defer non-critical components ([#494](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/494)) ([53b273e](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/53b273e8042abae07595d9a2f185418be73408c4))


### Documentation

* add comprehensive Mermaid documentation for backend SQL database architecture ([#237](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/237)) ([86af077](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/86af077d7be74c8b7ec5f7cccb3f5ab96e7c5312))
* **backend:** improve Swagger docs and Pydantic field descriptions for open-access data science audience ([#518](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/518)) ([bdff67c](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/bdff67c6f0c8c1ae0d0bc4ee249854147ababd53))
* update README, AGENTS docs and rename env blueprints ([#519](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues/519)) ([91818ed](https://github.com/Choice-of-Law-Dataverse/cold-web-app/commit/91818ed521af00a67c6213a85f375489374be48a))


## Intro

* [Playwright](https://playwright.dev) is a useful library to run UI test as
unit testing over a browser
<br></br>

* You can run/launch that supported browser (Chromium, Firefox, Webkit, etc.)
locally and use the `playwright` library to work/unit-test with it
<br></br>

* Or you can run a [docker container](https://playwright.dev/docker) acting
as the browser running on any machine and use the `playwright` library to
still work/unit-test with it that without having to launch anything locally
<br></br>

  * But just pointing to that docker container via `ws://host:port` url
  * More info about the `npx playwright ...` options
  [within the docs](https://playwright.dev/docs/ci)
  * See the [source `Dockerfile`](https://github.com/microsoft/playwright/blob/main/utils/docker/Dockerfile.noble)
  for additional details



## Explore

* First explore the `browsers` folder to run the different browsers in detached
and independent way as docker containers
<br></br>

* Then explore the `clients` folder to use the `playwright` library as client
execution via websockets against those previously deployed docker containers

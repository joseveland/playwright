

## Run your testing code against Playwright's online browsers

* Install dependencies
    ```shell
    pip install -r requirements.txt
    ```

* Make sure to change the `ws://host:port` URL of the demo clients
to point your running "playwright-server" docker container
<br></br>
  * Deployed locally you would typically use `ws://localhost:8080`
<br></br>
  * Deployed remotely you can have a public IP address if enabled as part
  of the ECS service's `assignPublicIp` vpc configuration
<br></br>
    * Make sure your VPC configuration has public subnets (subnets accessing
    the default internet gateway in AWS)
    * And also a security group with enough router table permissions/rules
    to allow inbound traffic for the `8080` port
    * Finally, in your python code you will typically use `ws://some-public-ip:8080`
    * BE CAREFUL as this is public and anyone can use this
<br></br>
  * Deployed remotely there is also has a private IP address that you can
  consume with a logic living in the same cloud; that is a python logic
  running inside a lambda pointing to `ws://some-private-ip:8080`
<br></br>

* Sync version that consumes the previously launched browser at 8080 port
    ```shell
    python main_sync.py
    ```

* Async version, but the same history
    ```shell
    python main_async.py
    ```


## Run your testing code as a Lambda

* Build the image locally
    ```shell
    docker build -t playwright-client .
    ```

* Running Lambda's RIE locally is possible but for it to reach the
playwright server locally you should create a shared docker network
  ```shell
  docker network create shared_net
  docker run -it --rm --network shared_net --name browsers --hostname browsers playwright-server
  docker run -it --rm --network shared_net -p 8090:8080 --name lambda playwright-client
  ```
  **NOTE:** I'm using a previously built `playwright-server` to runt the browsers
  as independent service, and a common network for the 
<br></br>

  * Consume that RIE locally too at another terminal
    ```shell
    curl "http://localhost:8090/2015-03-31/functions/function/invocations" \
      -H "content-type: application/json" \
      -d '{"browsers": "ws://browsers:8080", "target": "https://www.google.com"}' \
      -w "\n%{http_code}\n"
    ```

* Deploying to cloud (AWS)
<br></br>

  * Make sure your credentials are refreshed and create the remote ECR
  repository **once**
    ```shell
    aws sso login
    aws ecr --profile YOUR_LOCAL_PROFILE_NAME create-repository \
      --repository-name "playwright-client"
    ```

    * re-Tag your local image to be loadable into your AWS account/region
    values that you need (like `YOUR_ACCOUNT_ID`, `YOUR_REGION`) and push that
      ```shell
      docker tag \
        "playwright-client" \
        "YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-client"
    
      docker push \
        "YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-client"
      ```
    
  * Run a Lambda service using that uploaded image:
    ```shell
     aws lambda --profile YOUR_LOCAL_PROFILE_NAME \
      create-function \
      --function-name "jvelandia-playwright-client" \
      --package-type Image \
      --code "ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-client:latest" \
      --role "arn:aws:iam::YOUR_ACCOUNT_ID:role/gdr-agent-role" \
      --timeout 60 
    ```
    **NOTE:** make sure to change the placeholder UPPERCASE values with your
    own local setup and desired lambda role to use;
    but also the image URI and ARN because that is just a demo of a previously
    uploaded image and `YOUR_ACCOUNT_ID` might not be your own AWS account
<br></br>
    **NOTE:** to deploy a lambda the full tag is needed so `:latest` or
    any other is important
<br></br>

    * The lambda might need some VPC attachments to really see the ECS
    deployment of the `playwright-server` image already at AWS servers
    using private IP address (and therefore private subnets and some
    default security group for outbound rules)
      ```shell
      aws lambda --profile YOUR_LOCAL_PROFILE_NAME \
        update-function-configuration \
        --function-name "jvelandia-playwright-client" \
        --vpc-config "SubnetIds=subnet-aaa,subnet-bbb,subnet-ccc,SecurityGroupIds=sg-zzz
      ```

  * Consume the lambda with your desired payload:
    ```shell
    B64_PAYLOAD=$(python3 -c 'import json, base64; payload = {"browsers": "ws://10.0.161.75:8080", "target": "https://www.google.com"}; print(base64.b64encode(json.dumps(payload).encode()).decode())')
    
    aws lambda --profile YOUR_LOCAL_PROFILE_NAME \
      invoke \
      --function-name "jvelandia-playwright-client" \
      --invocation-type "RequestResponse" \
      --log-type "Tail" \
      --payload "${B64_PAYLOAD}" \
      --output "json" \
      result.json
    
    cat result.json   # To see the decoded response from lambda resource
    ```
    **NOTE:** change the `10.0.161.75` IP with your previous cloud deployment
    of the `playwright-server` at ECS, while making sure that task is really
    running as they can re-deploy and change its private IP address
<br></br>

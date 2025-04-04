

## Run Playwright browsers in Docker

* Build the [official docs](https://playwright.dev/docker) image as a local
one for you to use
    ```shell
    docker build -t playwright-server .
    ```

* Run that built image locally (for now but it can run at any other place)
    ```shell
    docker run -it --rm -p 8080:8080 playwright-server
    ```
  
    * From this point on you can test your client logic against localhost
    see [the client README](../client/README.md)
<br></br>
  
* Deploying to cloud (AWS)
<br></br>

  * Make sure your credentials are refreshed and create the remote ECR
  repository **once** with your own `YOUR_LOCAL_PROFILE_NAME`
    ```shell
    aws sso login
    aws ecr --profile YOUR_LOCAL_PROFILE_NAME create-repository \
      --repository-name "playwright-server"
    ```

    * re-Tag your local image to be loadable into your AWS account/region
    values that you need (like `YOUR_ACCOUNT_ID`, `YOUR_REGION`) and push that
      ```shell
      docker tag \
        "playwright-server" \
        "YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-server"
    
      docker push \
        "YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-server"
      ```
    
  * Run an ECS service using that uploaded image:
<br></br>
  
    * Create a log group `/ecs/services/playwright-serving` needed for the
    upcoming task definition at [ecs-task.json](ecs-task.json)
      ```shell
      aws logs --profile YOUR_LOCAL_PROFILE_NAME \
        create-log-group \
        --log-group-name /ecs/services/playwright-serving \
        --region YOUR_REGION
      ```
      **NOTE:** Don't forget to change `YOUR_LOCAL_PROFILE_NAME`
      with your desired local profile setup pointing to a specific account,
      region, etc. If working without region specification but environment
      variable credentials you can always specify a `--region` at this and
      upcoming AWS-cli commands
<br></br>
  
    * Create an ECS cluster `playwright-server-cluster` (Fargate, simpler)
      ```shell
      aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
        create-cluster \
        --cluster-name playwright-server-cluster \
        --region YOUR_REGION
      ```

      * Some status is always useful to verify the command above did something
        ```shell
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          describe-clusters \
            --clusters playwright-server-cluster
            --inlcude STATISTICS \
            --region YOUR_REGION
        ```
    * **MAKE SURE TO CHANGE** certain stuff inside [ecs-task.json](ecs-task.json)
<br></br>
      * Change log's `region`  value if needed
<br></br>
      * Change the demo image name ARN `YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/playwright-serve`
      with the one previously uploaded to ECR
<br></br>
      * Change the demo role `arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ECS_TASK_DEPLOYMENT_ROLE`
      and `arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ECS_EXECUTION_ROLE`
      with valid roles in your AWS ecosystem; probably both being 1 role
      with al required permissions/policies, so it does everything like:
<br></br>
        * The unified role should be able to create logs for execution, and some
        ECR access for task deployments, etc. For example these two policies inside:
          ```json
          {
              "Version": "2012-10-17",
              "Statement": [
                  {
                      "Effect": "Allow",
                      "Action": [
                          "ecr:GetAuthorizationToken",
                          "ecr:BatchCheckLayerAvailability",
                          "ecr:GetDownloadUrlForLayer",
                          "ecr:BatchGetImage",
                          "logs:CreateLogStream",
                          "logs:PutLogEvents"
                      ],
                      "Resource": "*"
                  }
              ]
          }
          ```
          ```json
          {
              "Version": "2012-10-17",
              "Statement": [
                  {
                      "Action": [
                          "logs:CreateLogGroup",
                          "logs:CreateLogStream",
                          "logs:PutLogEvents"
                      ],
                      "Effect": "Allow",
                      "Resource": "*"
                  }
              ]
            }
          ```

    * Create the task definition `playwright-task:X` based on the previously
    modified [ecs-task.json](ecs-task.json) according to your needs
      ```shell
      aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
        register-task-definition \
        --cli-input-json file://ecs-task.json \
         --region YOUR_REGION
      ```
      **NOTE:** The above will give you a task definition number created
      like `playwright-task:1` which late will be used on the service's
      creation/update
<br></br>

      * Some status is always useful to verify the command above did something
        ```shell
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          describe-task-definition \
            --task-definition playwright-task:1 \
            --region YOUR_REGION
        ```

    * Finally, create a service `playwright-service` using that previously
    created, cluster, task definition and some additional network/VPC
    configuration for this FARGATE deployment
      ```shell
      aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
        create-service \
          --service-name playwright-service \
          --cluster playwright-server-cluster \
          --task-definition playwright-task:X \
          --desired-count 1 \
          --launch-type FARGATE \
          --region YOUR_REGION \
          --network-configuration "awsvpcConfiguration={
              subnets=[
                  subnet-aaa,
                  subnet-bbb,
                  subnet-ccc,
              ],
              securityGroups=[
                  sg-zzz
              ],
              assignPublicIp=DISABLED
          }"
      ```
      **NOTE:** Change `playwright-task:X` with the last task definition
      given by the `aws ecs register-task-definition ...` command/creation
<br></br>
      **NOTE:** The `subnet-...` used will be related to a specific
      VPC that you want to use inside your AWS environment
<br></br>
      **NOTE:** The `sg-...` used will be related to a specific set
      of rules that should allow traffic against **8080** port to really
      use a public IP address
<br></br>
      **NOTE:** The `assignPublicIp` is optional and can be changed to
      `DISABLED` to avoid exposing these ECS containers/task to the outside
      world
<br></br>

      * Some status is always useful to verify the command above did something
        ```shell
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          describe-services \
            --cluster playwright-server-cluster \
            --services playwright-service \
            --region YOUR_REGION
        ```

    * If you want to modify your service for some reason after creation you
    could:
<br></br>

      * Maybe you have a new task definition like `playwright-task:Y`, so you
      can update your service to serve that instead by running:
        ```shell
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          update-service \
            --cluster playwright-server-cluster \
            --service playwright-service \
            --task-definition playwright-task:Y \
            --region YOUR_REGION
        ```

      * Or update the networking configuration also, etc:
        ```shell
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          update-service \
            --cluster playwright-server-cluster \
            --service playwright-service \
            --region YOUR_REGION \
            --network-configuration "awsvpcConfiguration={
                subnets=[
                    subnet-aaa,
                    subnet-bbb,
                    subnet-ccc,
                ],
                securityGroups=[
                    sg-zzz
                ],
                assignPublicIp=DISABLED
            }"
        ```

* Get info about the private IP addresses of the previously deployed
(and hopefully running after some setup and deployment time) tasks
(only 1 because I used `--desired-count 1`) once they are up and running like:
    
    ```shell
    aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
      list-tasks \
      --cluster playwright-server-cluster \
      --service playwright-service \
      --query "taskArns[]" \
      --output text | \
      while read taskArn; do
        aws ecs --profile YOUR_LOCAL_PROFILE_NAME \
          describe-tasks \
          --cluster playwright-server-cluster \
          --tasks $taskArn \
          --query "tasks[].{
            TaskARN:taskArn,
            PrivateIP:attachments[].details[?name=='privateIPv4Address'].value | [0],
            Status:lastStatus
          }" \
          --output json
      done
    ```
  
* You can also use the AWS console to graphically enter the ECS cluster,
then the ECS service, and finally the running ECS task, look for IPs into
the network tab
<br></br>

* Use that IP address to later run the demo clients, see
[its README](../client/README.md) for more info
<br></br>

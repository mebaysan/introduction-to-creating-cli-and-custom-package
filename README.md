# Introduction

Created by [@mebaysan](https://www.github.com/mebaysan)

I created this repo to have an idea about how we can create custom Python packages and how we can create CLIs by using [Click](https://click.palletsprojects.com/).

You can go to the custom `baysan-data-shortcuts` package that I created for this repo by using [here](./baysan_data_shortcuts/).

I created CLI in the `main.py` file.

`process` folder contains the some functions to use our package I mentioned above. I tried to simulate the processes of the CLI.


## Extra Content
You can check the other repo that I created about "Introduction to CI and CD on AWS and Google Cloud Platform with Flask" by using it [here](https://github.com/mebaysan/IntroductionToCloudComputingCI_CD). In this repo, we dived into;
- Makefile
- GitHub Actions
- AWS: Cloud9 & EC2
- Google Cloud Platform: Cloud Build & App Engine

---

Also, you can check my Medium story that I wrote detailed with step-by-step examples about the content above by using [here](https://medium.com/codex/introduction-to-continuous-integration-and-continuous-delivery-with-python-flask-a2fa1d48db6c).



# Setup

After creating a virtual environment, you can install the dependencies of the CLI by using the command below.
```bash
make install
```


# Usage
We can execute a CLI like the code below.
```bash
python main.py --param1 'Value1' --param2 12
```
We need to provide the following to execute our CLI:
- start_date
- end_date
- rfm_date
- statistics_date

We can execute the code below to get help about our CLI:
```bash
python main.py --help
```


## Example
```bash
python main.py --start_date '20210101' --end_date '20220207' --rfm_date '2022-01-31' --statistics_date '2022-01-31'
```

If we do as executable our `main.py` file, we can execute the code below.

```bash
./main.py --start_date '20210101' --end_date '20220207' --rfm_date '2022-01-31' --statistics_date '2022-01-31'
```

## How We Can Do as Executable Our Script
We have to put `#! virtualenv_path/bin/python` into the first line of `main.py` file. Then the computer will understand it needs to use the Python that we referred in the first line. 

Now we need to execute the script below to do as executable our file.
```bash
chmod +x main.py
```
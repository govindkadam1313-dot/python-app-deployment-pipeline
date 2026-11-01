# Python app deployment pipeline

This folder contains a small Flask application and a GitHub Actions workflow that copies it to an existing AWS EC2 instance and runs it as a `systemd` service.

## What is in this folder?

- `app.py` - The sample website (`/`) and a health endpoint (`/health`).
- `requirements.txt` - The Python packages installed on the EC2 instance.
- `.github/workflows/deploy.yml` - Deploys on every push to `main`, or when you start it manually from the Actions tab.

## Before you start

The workflow expects an already-created, running EC2 instance. It does not create AWS infrastructure.

Make sure:

1. The instance is reachable from GitHub Actions over SSH (TCP port 22). Restrict SSH access as much as your setup allows.
2. The instance has Python 3.9 or newer, its `venv` support, `pip`, `systemd`, and `sudo` installed. The SSH user must be allowed to run `sudo systemctl` and `sudo tee` without an interactive password.
3. The instance security group allows inbound TCP port `8000` from the client IP ranges that need to view the demo. Avoid opening this port to the whole internet for a real service; put a reverse proxy/load balancer in front instead.
4. You have the matching private key for the EC2 key pair. Add only the private key to GitHub; never commit it to this repository.

The package-install command depends on the operating system/AMI. For example, Ubuntu commonly uses `sudo apt install python3 python3-venv`, while Amazon Linux commonly uses `sudo dnf install python3` (older versions may use `yum`). Confirm the correct command for your AMI before deploying.

## Add GitHub Actions secrets

In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value to provide |
| --- | --- |
| `AWS_ROLE_ARN` | The ARN of the AWS IAM role that trusts GitHub Actions through the GitHub OIDC provider. |
| `EC2_HOST` | Your EC2 public DNS name or public IP address. |
| `EC2_USER` | SSH login user for your AMI, for example `ubuntu` or `ec2-user`. Update this to match your instance. |
| `EC2_SSH_PRIVATE_KEY` | The private SSH key that matches the key pair attached to the instance. Paste the complete key, including its BEGIN/END lines. |
| `EC2_KNOWN_HOSTS` | A trusted SSH host-key entry for the EC2 host. Populate this from a trusted source; do not disable SSH host-key checking. The entry normally starts with the exact host name/IP used in `EC2_HOST`, followed by the key type and public host key. |

Do not put secret values in the workflow file, README, or application source. Never share or commit your private key.

The workflow requests an OIDC token (`id-token: write`), assumes `AWS_ROLE_ARN`, and verifies the AWS identity. Configure the GitHub OIDC identity provider and the role's trust policy in AWS to trust only this repository (and, ideally, this deployment branch/environment). This identity check needs no additional AWS permissions; grant the role only the permissions needed if you later add AWS API operations.

OIDC authenticates the workflow to AWS; it does not log in to the EC2 operating system or provide the EC2 address. This workflow still deploys over SSH, so keep `EC2_HOST`, `EC2_USER`, `EC2_SSH_PRIVATE_KEY`, and `EC2_KNOWN_HOSTS` as GitHub Actions secrets. `EC2_USER` is the Linux account for your AMI; `EC2_HOST` is the public DNS/IP that GitHub Actions can reach. The host entry in `EC2_KNOWN_HOSTS` must match the host value used by `EC2_HOST`.

## Deploy

1. Put the contents of this folder in the root of your GitHub repository. The workflow file must be at `.github/workflows/deploy.yml` relative to that repository root.
2. Add the five repository secrets above.
3. Push to the `main` branch, or open **Actions → Deploy Python app to EC2 → Run workflow**.
4. Open `http://YOUR_EC2_PUBLIC_HOST:8000/` to see the page. Check `http://YOUR_EC2_PUBLIC_HOST:8000/health` for the health response.

## Values to review/update for your instance

- **AMI / Linux distribution:** Use the correct SSH username and install Python/venv using the commands for your AMI.
- **Network access:** The example listens on port `8000`. If you change it, update `Environment=PORT=8000` in the workflow and the EC2 security-group rule.
- **Deployment branch:** The workflow currently runs automatically for pushes to `main`. Change that branch name in the workflow if your default branch is different.
- **App service:** The workflow creates `/etc/systemd/system/python-app.service` and restarts it. The SSH user needs passwordless `sudo` for `systemctl` and writing this service file.
- **Production use:** This is a learning example using Flask's development server. For production, use a production WSGI server (such as Gunicorn) behind a reverse proxy or load balancer, with HTTPS and appropriately restricted network access.

If a value specific to your instance is unknown, update the matching secret or setting above; do not add credentials to the files in this folder.

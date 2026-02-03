# **LocalHelp**
**LocalHelp** is a web application developed in **Flask** that connects people in need with available volunteers in their area.

**The goal** is to foster local solidarity by supporting those who are unable to be completely self-sufficient, such as the elderly or people with mobility difficulties.

There are two main roles within the system:
- **Requester**: enters a request for help and assigns the completion of a successful request.
- **Volunteer**: views and accepts requests.

________________________________________
### **_Main Features_**
- User Registration and Login
- Posting Help Requests
- Viewing Available Requests on the Dashboard
- Accepting a Request from a Volunteer
- Managing Tasks Accepted:
  - Ongoing Tasks
  - Completed Tasks
- Managing Your Uploaded Requests:
  - Ongoing Requests (Accepted by a Volunteer) Completing the Request Using the appropriate Button
  - Completed Requests
  - Requests Not Yet Accepted
- Direct Link to Google Maps for the Address
________________________________________
### **_Technologies Used_**
- **Backend**: Python, Flask, JavaScript (API Fetch)
- **Frontend**: HTML, Jinja2, Bootstrap 5, JavaScript, CSS
- **Database**: SQLite (WAL enabled)
- **Other**: PWA (manifest + Service Worker)
________________________________________
### **_Project Structure_**
~~~
LocalHelp
│
├── LocalHelp.py                #Main Flask Application
├── templates/                  #HTML Templates (Jinja2)
│ ├── base.html
│ ├── requests.html
│ ├── noticeboard.html
│ ├── add.html
│ ├── _card_template.html
│ ├── activities.html
│ ├── login.html
│ └── register.html
│
├── static/                     #File static
│ ├── CSS/
│ │ └── style.css               #Stylesheet
│ ├── js/
│ │ └── main.js                 #Registration sw.js
│ ├── icons/
│ │ └── icon-192.png
│ │ └── icon-512.png
│ ├── manifest.js               #Manifest
│ └── sw.js                     #Service_workwer
│
├── requirements.txt            #Python dependencies
└── README.md                   #Documentation
~~~

________________________________________
### **_Installation_**
#### Clone the repository

```sh
git clone https://github.com/GiuseppeSaccavino/LocalHelp.git
cd LocalHelp
```

#### Creating the virtual environment
To create the virtual environment, go to the `Localhelp` folder and run one of the two commands below in the terminal.
```sh
python -m venv venv
```
``` sh
python3 -m venv venv
```
#### Activating the virtual environment
Once the virtual environment has been created, activate it with one of the commands below, depending on the system you are using.
```sh
source venv/bin/activate        # macOS/Linux
```
```sh
venv\Scripts\activate           # Windows
```
#### Install dependencies
```sh
pip install -r requirements.txt
```
#### Set environment variables for Flask
```sh
export FLASK_APP=LocalHelp.py   # macOS/Linux
```
```sh
set FLASK_APP=LocalHelp.py      # Windows
```
```sh
export FLASK_ENV=development    # (optional for debugging)
```

#### Start the application
With the virtual environment active and running the commands from the project directory:
```sh
flask run   #Starts the application on the default port 5000 (if available).
```

Open your browser at: `http://127.0.0.1:5000`

You can specify the port and host:
```sh
flask --app LocalHelp run --port <port> --host <host_ip>
```

`--port <port>`: port to use (other than the free 5000).

`--host <host_ip>`: allows access from the local network via `http://<host_ip>:<port>`.

`--host 0.0.0.0`: enables access from all devices on the same local network using `http://<IP_PC_SERVER>:<port>`.

Example:
```sh
flask --app LocalHelp run --host 0.0.0.0 --port 8000
```
________________________________________
#### Important Notes
> [!NOTE]
>- The first time you run it, it may take a few seconds to start due to database initialization.
>- Form validation occurs both on the client side (`HTML5`) and on the server side.
>- The interface is responsive thanks to `Bootstrap 5.3.2`.
>- The `SQLite database` uses **WAL** to reduce crashes in the event of concurrent access.
________________________________________
#### Python Version
>[!TIP]
>Recommended: **Python 3.11+**
>Tested on:
>- `Windows 3.11`
>- `Linux Mint 3.12`

________________________________________
### **_LICENSE_**
This project is released under the MIT License.

See the [LICENSE](LICENSE) file for details.


import requests # get the requsts library from https://github.com/requests/requests
import os
import platform
import shutil
from netrc import netrc
from subprocess import Popen
from getpass import getpass

# overriding requests.Session.rebuild_auth to mantain headers when redirected
class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)
 
   # Overrides from the library to keep headers when redirected to or from the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:
                    del headers['Authorization']
        return

def create_validation_files(homeDir,urs,username,password):
    """

    
    """
    with open(homeDir + '.netrc', 'w') as file:
        file.write('machine {} login {} password {}'.format(urs, username, password))
        file.close()
    with open(homeDir + '.urs_cookies', 'w') as file:
        file.write('')
        file.close()
    with open(homeDir + '.dodsrc', 'w') as file:
        file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
        file.write('HTTP.NETRC={}.netrc'.format(homeDir))
        file.close()
    print('Done with creating the required validation files!')
    print('Saved .netrc, .urs_cookies, and .dodsrc to:', homeDir)
    # Set appropriate permissions for Linux/macOS
    if platform.system() != "Windows":
        Popen('chmod og-rw ~/.netrc', shell=True)
    else:
        # Copy dodsrc to working directory in Windows  
        shutil.copy2(homeDir + '.dodsrc', os.getcwd())
        print('Copied .dodsrc to:', os.getcwd())

def extract_earthdata(username,password):
    """
    
    """
    # create session with the user credentials that will be used to authenticate access to the data
    session = SessionWithHeaderRedirection(username, password)
    # the url of the file we wish to retrieve
    url = "https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2I1NXINT.5.12.4/2022/01/MERRA2_400.inst1_2d_int_Nx.20220101.nc4"
    # extract the filename from the url to be used when saving the file
    filename = url[url.rfind('/')+1:]  
    try:
        # submit the request using the session
        response = session.get(url, stream=True)
        print(response.status_code)
        # raise an exception in case of http errors
        response.raise_for_status()  
        # save the file
        with open(filename, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):
                fd.write(chunk)
    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)

urs = 'urs.earthdata.nasa.gov'    # Earthdata URL to call for authentication
homeDir = os.path.expanduser("~") + os.sep
# Username and password should be defined in the os environment variables
try:
    username = os.environ.get('SecretUser')
    password= os.environ.get('SecretPassword')
    if username and password is not None:
        print("Username and Password is exists in your environment variables, Proceeding with the validation process!")
    else:
        raise Exception("'SecretUser' and 'SecretPassword' aren't exists in your environment variables, please set them first to be able to continue!")
    create_validation_files(homeDir,urs,username,password)
    extract_earthdata(username,password)
except Exception as e:
    raise
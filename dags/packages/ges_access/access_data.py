import requests
import os
import platform
import shutil
from netrc import netrc
from subprocess import Popen
from getpass import getpass
import netCDF4 as nc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np


# overriding requests.Session.rebuild_auth to maintain headers when redirected
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

def _create_validation_files(homeDir,urs,username,password):
    """
        Create the required files for authinticating user in ges-disc website
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

def _extract_earthdata(username,password,ti):
    """
        Extract ges-disc satalite ocean temperature data from nasa website
    """
    # create session with the user credentials that will be used to authenticate access to the data
    session = SessionWithHeaderRedirection(username, password)
    # the url of the file we wish to retrieve
    url = "https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXSLV.5.12.4/2022/01/MERRA2_400.tavg1_2d_slv_Nx.20220101.nc4"
    # extract the filename from the url to be used when saving the file
    filename = url[url.rfind('/')+1:]  
    try:
        # submit the request using the session
        response = session.get(url, stream=True)
        print(response.status_code)
        # raise an exception in case of http errors
        response.raise_for_status()  
        # save the file inside downloaded_files
        folder_name = "downloaded_files/"
        is_exist = os.path.exists(folder_name)
        if not is_exist:
            os.makedirs(folder_name)
            
        full_path = folder_name + filename
        ti.xcom_push(key='full_file_path',value=full_path)
        with open(full_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):
                fd.write(chunk)
    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)

def _create_temp_png_file(ti):
    """
        Create a png file based on the satalite data of air tempreture from NASA
    """
    source_path= ti.xcom_pull(key="full_file_path",task_ids='extract_earthdata')
    ds = nc.Dataset(source_path,mode='r')
    lons = ds.variables['lon'][:]
    lats = ds.variables['lat'][:]
    T2M = ds.variables['T2M'][:,:,:]
    T2M = T2M[0,:,:]
    
    fig = plt.figure(figsize=(8,4))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.set_global()
    ax.coastlines(resolution="110m",linewidth=1)
    ax.gridlines(linestyle='--',color='blue')

    # Set contour levels, then draw the plot and a colorbar
    clevs = np.arange(230,311,5)
    plt.contourf(lons, lats, T2M, clevs, transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
    plt.title('MERRA-2 Air Temperature at 2m, January 2022', size=14)
    cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
    cb.set_label('K',size=12,rotation=0,labelpad=15)
    cb.ax.tick_params(labelsize=10)

    # Save the plot as a PNG image
    output_file = 'output_png_files/MERRA2_t2m.png'
    if not os.path.exists('output_png_files'):
        os.makedirs('output_png_files')
    fig.savefig(output_file, format='png', dpi=360)
    
    
def _get_user_cridetials():
    """
        Get the user cridentials that defined in the os environment variables
    """
    try:
        username = os.environ.get('SecretUser')
        password = os.environ.get('SecretPassword')
        if username and password is not None:
            print("Username and Password is exists in your environment variables, Proceeding with the validation process!")
            return (username,password)
        else:
            raise Exception("'SecretUser' and 'SecretPassword' aren't exists in your environment variables, please set them first to be able to continue!")
    except Exception as e:
        raise
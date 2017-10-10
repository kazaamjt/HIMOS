from distutils.core import setup
import py2exe, sys , os

mydata_files = []
mydata_files.append(('.',['C:\\Python34\\Lib\\site-packages\\Python.Runtime.dll']))

setup(
	data_files=mydata_files,
	console=['HIMOS-Client.py'],
	options = {
		'py2exe' : {
				'packages' : ['requests','jsonpickle'],
				'includes' : ['clr'],
				'bundle_files': 1
			}
		}
)

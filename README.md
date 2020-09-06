# intelligentRoutingFramework

Run these configurations and files on fedora 29:

1-	Install openvswitch, python-devel, cpu-limit
  dnf install python-devel
  dnf install cpu-limit
  dnf install openvswitch
  systemctl restart openvswitch.service
  systemctl enable openvswitch.service

2-	Install mininet and pox
  git clone git://github.com/mininet/ mininet
  cd mininet
  util/install.sh –mnp

3-	Install Snort from www.snort.org
 
4-	Install pip and python 2.7 packages
  pip install numpy
  pip install psutil
  pip install csv
  pip install dijkstar

5-	copy our intelligent routing framework from github
  git clone git://github.com/zadkhosh/intelligentRoutingFramework.git
  
  NOTE: in the downloaded files (InitializeFramework.py, CreateNetworkContainsMiddelBoxes.py, IntelligentRoutingFramework.py, Client1.py, Client2.py) change the mainpath to the path that you extract our project.
  
6-	copy IntelligentRoutingFramework.py to /usr/lib64/python2.7/side-packages/pox

7-	Run the intelligent routing framework (in two different terminals)
  (terminal 1) python CreateNetworkContainsMiddelBoxes.py
  (terminal 2) python InitializeFramework.py

8-	Test the intelligent routing framework
  In terminal 1 use xterm to have access to hosts and servers
  xterm h1, h2, h3, h4
  
  h1> python Client1.py
  h2> python Server1.py
  h3> python Client2.py
  h4> python Server2.py
  
  NOTE: Client1.py and Client2.py have 4 running threads.
  NOTE: Servers should be run before clients


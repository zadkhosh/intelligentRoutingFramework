import sys
sys.path.append('/usr/lib64/python2.7/site-packages/pox')
from pox import boot

def main():
    sys.argv.append('forwarding.IntelligentRoutingFramework')
    boot.boot()

if __name__=='__main__':
    main()
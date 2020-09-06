

mainPath = '/home/esi/mininetProject/networkFiles/'


from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def topology():
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSSwitch)
    print "*** Creating nodes"

    f1 = net.addSwitch('f1', dpid='00:00:00:00:00:00:00:05')
    f2 = net.addSwitch('f2', dpid='00:00:00:00:00:00:00:06')
    f3 = net.addSwitch('f3', dpid='00:00:00:00:00:00:00:07')
    f4 = net.addSwitch('f4', dpid='00:00:00:00:00:00:00:08')

    # f5 = net.addSwitch('f5', dpid='00:00:00:00:00:00:00:09')
    # f6 = net.addSwitch('f6', dpid='00:00:00:00:00:00:00:10')
    # f7 = net.addSwitch('f7', dpid='00:00:00:00:00:00:00:11')

    s1 = net.addSwitch('s1', dpid='00:00:00:00:00:00:00:01')
    s2 = net.addSwitch('s2', dpid='00:00:00:00:00:00:00:02')
    s3 = net.addSwitch('s3', dpid='00:00:00:00:00:00:00:03')
    s4 = net.addSwitch('s4', dpid='00:00:00:00:00:00:00:04')

    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')


    c1 = net.addController('c1', controller=RemoteController)

    print "*** Creating links"

    net.addLink(h1, s1, bw=1000)
    net.addLink(h2, s2, bw=1000)
    net.addLink(h3, s3, bw=1000)
    net.addLink(h4, s4, bw=1000)

    net.addLink(s1, f1, bw=4)
    net.addLink(s1, f2, bw=4)
    net.addLink(s1, f3, bw=4)
    net.addLink(s1, f4, bw=4)
    # net.addLink(s1, f5, bw=4)
    # net.addLink(s1, f6, bw=4)
    # net.addLink(s1, f7, bw=4)

    net.addLink(s2, f1, bw=4)
    net.addLink(s2, f2, bw=4)
    net.addLink(s2, f3, bw=4)
    net.addLink(s2, f4, bw=4)
    # net.addLink(s2, f5, bw=4)
    # net.addLink(s2, f6, bw=4)
    # net.addLink(s2, f7, bw=4)

    net.addLink(s3, f1, bw=1000)
    net.addLink(s3, f2, bw=1000)
    net.addLink(s3, f3, bw=1000)
    net.addLink(s3, f4, bw=1000)
    # net.addLink(s3, f5, bw=1000)
    # net.addLink(s3, f6, bw=1000)
    # net.addLink(s3, f7, bw=1000)

    net.addLink(s4, f1, bw=1000)
    net.addLink(s4, f2, bw=1000)
    net.addLink(s4, f3, bw=1000)
    net.addLink(s4, f4, bw=1000)
    # net.addLink(s4, f5, bw=1000)
    # net.addLink(s4, f6, bw=1000)
    # net.addLink(s4, f7, bw=1000)

    print "*** Starting network"
    net.build()
    c1.start()

    s1.start([c1])
    s2.start([c1])
    s3.start([c1])
    s4.start([c1])


    f1.start([c1])
    out = f1.cmd("sudo snort -D -dev -l " + mainPath + "log -i f1-eth3 ", verbose=True)
    f1Pid = out.split(" ")[5]
    f1.cmd("sudo cpulimit --pid " + str(f1Pid) + " --limit 4 & ", verbose=True)
    f2.start([c1])
    out = f2.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f2-eth3 ", verbose=True)
    f2Pid = out.split(" ")[5]
    f2.cmd("sudo cpulimit --pid " + str(f2Pid) + " --limit 4 & ", verbose=True)
    f3.start([c1])
    out = f3.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f3-eth3 ", verbose=True)
    f3Pid = out.split(" ")[5]
    f3.cmd("sudo cpulimit --pid " + str(f3Pid) + " --limit 4 & ", verbose=True)
    f4.start([c1])
    out = f4.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f4-eth3 ", verbose=True)
    f4Pid = out.split(" ")[5]
    f4.cmd("sudo cpulimit --pid " + str(f4Pid) + " --limit 4 & ", verbose=True)


    # f5.start([c1])
    # out = f5.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f5-eth3 ", verbose=True)
    # f5Pid = out.split(" ")[5]
    # f5.cmd("sudo cpulimit --pid " + str(f5Pid) + " --limit 4 & ", verbose=True)
    #
    # f6.start([c1])
    # out = f6.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f6-eth3 ", verbose=True)
    # f6Pid = out.split(" ")[5]
    # f6.cmd("sudo cpulimit --pid " + str(f6Pid) + " --limit 4 & ", verbose=True)
    #
    # f7.start([c1])
    # out = f7.cmd("sudo snort -D -dev -l  " + mainPath + "log -i f7-eth3 ", verbose=True)
    # f7Pid = out.split(" ")[5]
    # f7.cmd("sudo cpulimit --pid " + str(f7Pid) + " --limit 4 & ", verbose=True)


    firewallPID = open(mainPath + "firewallPID.txt", "w")
    firewallPID.write(str(net.nameToNode["f1"].dpid) + "," + f1Pid)
    firewallPID.write("\n")
    firewallPID.write(str(net.nameToNode["f2"].dpid) + "," + f2Pid)
    firewallPID.write("\n")
    firewallPID.write(str(net.nameToNode["f3"].dpid) + "," + f3Pid)
    firewallPID.write("\n")
    firewallPID.write(str(net.nameToNode["f4"].dpid) + "," + f4Pid)
    # firewallPID.write("\n")
    # firewallPID.write(str(net.nameToNode["f5"].dpid) + "," + f5Pid)
    # firewallPID.write("\n")
    # firewallPID.write(str(net.nameToNode["f6"].dpid) + "," + f6Pid)
    # firewallPID.write("\n")
    # firewallPID.write(str(net.nameToNode["f7"].dpid) + "," + f7Pid)
    firewallPID.close()

    topoFile = open(mainPath + "topoFile.txt","w")
    for i in range(net.links.__len__()):
        intf1 = str(net.links.__getitem__(i).intf1)
        intf2 = str(net.links.__getitem__(i).intf2)
        if (isinstance(net.nameToNode[intf1.split('-')[0]],Host)):
            ip1 = str(net.nameToNode[intf1.split('-')[0]].params['ip'])
        else:
            ip1 = str(net.nameToNode[intf1.split('-')[0]].dpid)
        if (isinstance(net.nameToNode[intf2.split('-')[0]], Host)):
            ip2 = str(net.nameToNode[intf2.split('-')[0]].params['ip'])
        else:
            ip2 = str(net.nameToNode[intf2.split('-')[0]].dpid)
        port1 = intf1.split('-')[1].split("eth")[1]
        port2 = intf2.split('-')[1].split("eth")[1]

        topoFile.write(ip1 + "," + port1 + "," + ip2)
        topoFile.write("\n")
        topoFile.write(ip2 + "," + port2 + "," + ip1)
        topoFile.write("\n")
    topoFile.close()
    print "*** Running CLI"
    CLI( net )
    print "*** Stopping network"

    f1.cmd("sudo kill " + f1Pid)
    f2.cmd("sudo kill " + f2Pid)
    f3.cmd("sudo kill " + f3Pid)
    f4.cmd("sudo kill " + f4Pid)
    # f5.cmd("sudo kill " + f5Pid)
    # f6.cmd("sudo kill " + f6Pid)
    # f7.cmd("sudo kill " + f7Pid)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()

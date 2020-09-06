

mainPath = '/home/esi/mininetProject/networkFiles/'


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.recoco import Timer

from dijkstar import Graph, find_path

import csv
import psutil
import numpy as np
import threading
import time

log = core.getLogger()
counter = 0
timeforUpdateCost = 2 #5
BWMiddleBox = 4
finalCost = 0
firstCost = 0

graphNodes = set()
middleBoxProcess = {}
portBetweenNodes = {}
costBetweenNodes = {}
cpuUsage = {}
memoryUsage = {}
bandWidthUsage = {}
tarnsmittedBayes_t1 = {}
receivedBayes_t1 = {}
finalCost_t1 = {}
firstCost_t1 = {}

tarnsBayes = {}

dilayNode = {}

distancesRoundRobin = {}

coefficent = {}
coefficent['cpu'] = .1;
coefficent['bw'] = .9;
coefficent['mem'] = 0;

def initializeSDN():
  global mainPath,graphNodes,middleBoxProcess,\
    portBetweenNodes,costBetweenNodes,\
    cpuUsage,memoryUsage,bandWidthUsage,\
    tarnsmittedBayes_t1,receivedBayes_t1,\
    distancesRoundRobin
  # read topology of graph
  topoFile = open(mainPath + "topoFile.txt", "r")
  topoReader = csv.reader(topoFile)
  for row in topoReader:
    node1 = row[0]
    node2 = row[2]
    port = row[1]

    if node1 not in graphNodes:
      graphNodes.add(node1)
      portBetweenNodes[node1] = {}
      costBetweenNodes[node1] = {}
      cpuUsage[node1] = {}
      memoryUsage[node1] = {}
      bandWidthUsage[node1] = {}
      tarnsmittedBayes_t1[node1] = {}
      tarnsBayes[node1] = {}
      receivedBayes_t1[node1] = {}
      finalCost_t1[node1] = {}
      firstCost_t1[node1] = {}
      distancesRoundRobin[node1] = {}
      dilayNode[node1] = {}

    portBetweenNodes[node1][node2] = port
    costBetweenNodes[node1][node2] = 0.0
    cpuUsage[node1][node2] = 0.0
    memoryUsage[node1][node2] = 0.0
    bandWidthUsage[node1][node2] = 0.0
    tarnsmittedBayes_t1[node1][node2] = 0.0
    receivedBayes_t1[node1][node2] = 0.0
    finalCost_t1[node1][node2] = 0.0
    firstCost_t1[node1][node2] = 0.0
    distancesRoundRobin[node1][node2] = 0.0
    tarnsBayes[node1][node2] = 0.0
    dilayNode[node1][node2] = 0.0

  topoFile.close()

  # read process id of middelBoxes
  middelBoxPIDFile = open(mainPath + "firewallPID.txt", "r")
  middelBoxPIDReader = csv.reader(middelBoxPIDFile)
  for row in middelBoxPIDReader:
    middelBox = row[0]
    processId = row[1]
    middleBoxProcess[middelBox] = int(processId)
  middelBoxPIDFile.close()

  costLogFile = open(mainPath + "costLog.txt", "w")
  bwLogFile = open(mainPath + "costLogBW.txt", "w")
  cpuLogFile = open(mainPath + "costLogCPU.txt", "w")
  ramLogFile = open(mainPath + "costLogRAM.txt", "w")
  idx = 0
  header = ""
  for node1 in costBetweenNodes.keys():
    for node2 in costBetweenNodes[node1].keys():
      if (idx != 0):
        header += ","
      header += str(node1) + "-" + str(node2)
      idx += 1

  header += "\n"
  costLogFile.writelines(header)
  bwLogFile.writelines(header)
  cpuLogFile.writelines(header)
  ramLogFile.writelines(header)
  costLogFile.close()
  bwLogFile.close()
  cpuLogFile.close()
  ramLogFile.close()


def requestForUpdateCost():
  global middleBoxProcess
  for con in core.openflow._connections.values():
    nodeName = str(con).split("-")[-1].split(" ")[0]
    for i in range(16 - len(nodeName)):
      nodeName = "0" + nodeName

    if (nodeName in middleBoxProcess.keys()):  # just for middelBoxes
      con.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    if (nodeName == "0000000000000002" or nodeName == "0000000000000001"):  # for sw2
      con.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

def roundRobin(src, dst, flag):
  global distancesRoundRobin

  if (flag == True and
          (#(src == "0000000000000001" and dst != "10.0.0.1/8") or
           (src == "0000000000000003" and dst != "10.0.0.3/8"))):
      nodeItem1=src

      keysNode2 = distancesRoundRobin[nodeItem1].keys()
      if("10.0.0.1/8" in keysNode2):
        keysNode2.remove("10.0.0.1/8")
      if("10.0.0.2/8" in keysNode2):
        keysNode2.remove("10.0.0.2/8")
      if ("10.0.0.3/8" in keysNode2):
        keysNode2.remove("10.0.0.3/8")
      if ("10.0.0.4/8" in keysNode2):
        keysNode2.remove("10.0.0.4/8")
      selectdIndx = -1
      indx = -1
      for nodeItem2 in keysNode2:
        indx += 1
        if(distancesRoundRobin[nodeItem1][nodeItem2]==1):
          selectdIndx = indx
        else:
          distancesRoundRobin[nodeItem1][nodeItem2] = 10

      if(selectdIndx==-1):
        distancesRoundRobin[nodeItem1][keysNode2[0]]=1
      else:
        distancesRoundRobin[nodeItem1][keysNode2[selectdIndx]] = 10
        distancesRoundRobin[nodeItem1][keysNode2[(selectdIndx+1) % len(keysNode2)]] = 1

  graph = Graph()
  for nodeItem1 in distancesRoundRobin.keys():
    for nodeItem2 in distancesRoundRobin[nodeItem1].keys():
      graph.add_edge(nodeItem1, nodeItem2, {'cost': distancesRoundRobin[nodeItem1][nodeItem2]})
  cost_func = lambda u, v, e, prev_e: e['cost']
  return find_path(graph, src, dst, cost_func=cost_func).nodes

class LoadBalancerMiddleBox (object):
  global middleBoxProcess, costBetweenNodes, \
    portBetweenNodes, graphNodes, mainPath,cpuUsage,\
    memoryUsage,bandWidthUsage,tarnsmittedBayes_t1,\
    receivedBayes_t1, counter, tarnsBayes, BWMiddleBox,\
    finalCost, finalCost_t1, firstCost, firstCost_t1, \
    dilayNode

  def __init__ (self, connection, transparent):
    self.connection = connection
    self.transparent = transparent
    connection.addListeners(self)


  def connectionNameToNodeName(self, con):
    nodeName = str(con).split("-")[-1].split(" ")[0]
    for i in range(16 - len(nodeName)):
      nodeName = "0" + nodeName
    return nodeName


  def findBestPath(self, src, dst):
    graph = Graph()
    for node1 in costBetweenNodes.keys():
      for node2 in costBetweenNodes[node1].keys():
        graph.add_edge(node1, node2, {'cost': costBetweenNodes[node1][node2]})
    cost_func = lambda u, v, e, prev_e: e['cost']
    return find_path(graph, src, dst, cost_func=cost_func).nodes


  def calculateUsedBandWidth(self, event, nodeName):
    stats = {}
    for st in event.stats:
      stats[st.port_no] = st

    node2 = nodeName
    for node1 in bandWidthUsage.keys():
      if (node2 in bandWidthUsage[node1].keys()):
        receivedBayes_t2 = stats[int(portBetweenNodes[node2][node1])].rx_bytes

        receiveBW = float(
          (((((receivedBayes_t2 - receivedBayes_t1[node1][node2]) / timeforUpdateCost) * 8.) / 1000000) / BWMiddleBox) * 100.)

        if (receivedBayes_t1[node1][node2] != 0):
          bandWidthUsage[node1][node2] = receiveBW

        receivedBayes_t1[node1][node2] = receivedBayes_t2



  def calculateUsedMemoryAndCpu(self, nodeName):
    cpu = float(psutil.Process(middleBoxProcess[nodeName]).cpu_percent(0.2))*15
    memory = float(psutil.Process(middleBoxProcess[nodeName]).memory_percent())
    node2 = nodeName
    for node1 in cpuUsage.keys():
      if (node2 in cpuUsage[node1].keys()):
        cpuUsage[node1][node2] = cpu
        memoryUsage[node1][node2] = memory

  def calculateCost(self, event, nodeName):
    global finalCost, finalCost_t1
    stats = {}
    for st in event.stats:
      stats[st.port_no] = st

    # transmitted bytes
    node2 = '10.0.0.2/8'
    node1 = "0000000000000002"
    finalCost_t2 = stats[int(portBetweenNodes[node1][node2])].tx_bytes
    if(finalCost_t1[node1][node2]!=0):
      finalCost += finalCost_t2 - finalCost_t1[node1][node2];
    finalCost_t1[node1][node2] = finalCost_t2;

  def calculateFirstCost(self, event, nodeName):
    global firstCost, firstCost_t1
    stats = {}
    for st in event.stats:
      stats[st.port_no] = st

    # transmitted bytes
    node2 = '10.0.0.1/8'
    node1 = "0000000000000001"

    firstCost_t2 = stats[int(portBetweenNodes[node1][node2])].rx_bytes
    if (firstCost_t1[node1][node2] != 0):
      firstCost += firstCost_t2 - firstCost_t1[node1][node2];
    firstCost_t1[node1][node2] = firstCost_t2;

  def logCost(self, cost, fileName):
    f = open(fileName, "a")
    line = ""
    idx = 0
    for node1 in cost.keys():
      for node2 in cost[node1].keys():
        if (idx != 0):
          line += ","
        line += str(cost[node1][node2])
        idx += 1

    line += "\n"
    f.writelines(line)
    f.close()


  def _handle_portstats_received(self, event):
    global counter
    nodeName = self.connectionNameToNodeName(event.connection)
    if(nodeName == "0000000000000002"):
      self.calculateCost(event, nodeName)
    elif(nodeName == "0000000000000001"):
      self.calculateFirstCost(event, nodeName)
    else:
      counter += 1
      self.calculateUsedBandWidth(event, nodeName)

      self.calculateUsedMemoryAndCpu(nodeName)

      for node1 in costBetweenNodes.keys():
        for node2 in costBetweenNodes[node1].keys():

            if (node2 in middleBoxProcess.keys() or node1 in middleBoxProcess.keys()):
              costBetweenNodes[node1][node2] =  (coefficent['cpu']*cpuUsage[node1][node2]) + (coefficent['mem']*memoryUsage[node1][node2]) + (coefficent['bw']*bandWidthUsage[node1][node2])
            else:
              costBetweenNodes[node1][node2] = 0

      if(counter==4):
        self.logCost(costBetweenNodes, mainPath + "costLog.txt")
        self.logCost(bandWidthUsage, mainPath + "costLogBW.txt")
        self.logCost(cpuUsage, mainPath + "costLogCPU.txt")
        self.logCost(memoryUsage, mainPath + "costLogRAM.txt")
        counter = 0


  def _handle_PacketIn (self, event):

    packet = event.parsed

    def drop (duration = None):
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if(str(packet.payload).find("{ipv")==-1):
      src = self.connectionNameToNodeName(event.connection)
      if(str(packet.payload).find("ARP")!=-1):
        dst = str(event.parsed.payload.protodst) + "/8"
      else:
        dst = str(event.parsed.payload.dstip) + "/8"
      if (src in graphNodes and dst in graphNodes):
        if(dst=="10.0.0.4/8" or dst=="10.0.0.3/8"):
          if (str(packet.payload).find("TCP") != -1):
            bestPath = roundRobin(src, dst, True)
          else:
            bestPath = roundRobin(src, dst, False)
        else:
          bestPath = self.findBestPath(src, dst)
        for i in range(1):
          port = int(portBetweenNodes[bestPath[i]][bestPath[i+1]])
          msg = of.ofp_flow_mod()
          #msg = of.ofp_packet_out()
          msg.match = of.ofp_match.from_packet(packet, event.port)
          msg.idle_timeout = 5 #5
          if (dst=="10.0.0.4/8" or dst=="10.0.0.3/8"):
            msg.hard_timeout = 6000 # 30
          else:
            msg.hard_timeout = 11  # 30

          msg.actions.append(of.ofp_action_output(port = port))
          msg.data = event.ofp # 6a
          event.connection.send(msg)

class l2_learning (object):
  global timeforUpdateCost, counter
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    global counter
    counter+=1
    log.debug("Connection %s" % (event.connection,))
    loadBalancer = LoadBalancerMiddleBox(event.connection, self.transparent)
    nodeName = loadBalancer.connectionNameToNodeName(event.connection)
    if(counter==6): # just for middelBoxes:
      core.openflow.addListenerByName("PortStatsReceived", loadBalancer._handle_portstats_received)
      Timer(timeforUpdateCost, requestForUpdateCost, recurring=True)
      counter = 0

import subprocess
import random
class GA(object):
  global finalCost, coefficent, finalCost_t1, firstCost, firstCost_t1

  NFE = 0;

  def Mutate(self, x, mu, VarMin, VarMax):

    nVar = len(x);

    nmu = np.ceil(mu * nVar);

    j = np.random.permutation(range(int(nVar)))[0];

    sigma = 0.1 * (VarMax - VarMin);

    y = x;
    y[j] = x[j] + sigma * np.random.randn();

    y[j] = max(y[j], VarMin);
    y[j] = min(y[j], VarMax);

    return y;

  def Crossover(self, x1, x2, gamma, VarMin, VarMax):

    alpha = np.random.uniform(-1 * gamma, 1 + gamma, np.size(x1));

    y1 = alpha * x1 + (1 - alpha) * x2;
    y2 = alpha * x2 + (1 - alpha) * x1;

    for i in range(len(x1)):
      y1[i] = max(y1[i], VarMin[i]);
      y1[i] = min(y1[i], VarMax[i]);

    for i in range(len(x1)):
      y2[i] = max(y2[i], VarMin[i]);
      y2[i] = min(y2[i], VarMax[i]);

    return [y1, y2];

  def RouletteWheelSelection(self, P):
    r = random.random();
    c = np.cumsum(P);
    f = np.where(r <= c);
    if (len(f[0]) != 0):
      i = f[0][0];
    else:
      i = 0;
    return i;

  def CostFunction(self, x):
    self.NFE += 1;
    print self.NFE;

    global finalCost, coefficent, finalCost_t1, firstCost, firstCost_t1

    coefficent['cpu'] = x[0];
    coefficent['bw'] = x[1];
    coefficent['mem'] = 0.0;
    print x;

    finalCost = 0;
    firstCost = 0;
    for node1 in finalCost_t1.keys():
      for node2 in finalCost_t1[node1].keys():
        finalCost_t1[node1][node2] = 0;
        firstCost_t1[node1][node2] = 0;
        dilayNode[node1][node2] = 0;


    subprocess.call(["ovs-ofctl", "del-flows", "s1"]);
    subprocess.call(["ovs-ofctl", "del-flows", "s2"]);
    subprocess.call(["ovs-ofctl", "del-flows", "s3"]);
    subprocess.call(["ovs-ofctl", "del-flows", "s4"]);

    subprocess.call(["ovs-ofctl", "del-flows", "f1"]);
    subprocess.call(["ovs-ofctl", "del-flows", "f2"]);
    subprocess.call(["ovs-ofctl", "del-flows", "f3"]);
    subprocess.call(["ovs-ofctl", "del-flows", "f4"]);


    time.sleep(180) #300

    out = (400000000 - finalCost) / 400000000.0 ;

    # time.sleep(5)

    print "---00000---"
    print finalCost
    print firstCost
    print out
    print "---00000---"

    return out;

  def runGA(self):
    time.sleep(10);
    nVar = 2;  # Number of Decision Variables

    VarSize = [1, nVar];  # Decision Variables Matrix Size

    VarMin = [0, 0];  # Lower Bound of Variables
    VarMax = [1, 1];  # Upper Bound of Variables

    ## GA Parameters

    MaxIt = 10 #200;  # Maximum Number of Iterations

    nPop = 9;  # Population Size

    pc = 0.6#0.8;  # Crossover Percentage
    nc = 2 * round(pc * nPop / 2);  # Number of Offsprings (Parnets)

    pm = 0.5#0.3;  # Mutation Percentage
    nm = round(pm * nPop);  # Number of Mutants

    gamma = 0.05;

    mu = 0.02;  # Mutation Rate

    beta = 8;

    # Initialization
    # pop = (position, cost)
    pop = [];
    cost_pop = [];
    for i in range(nPop):
      pop.append([0, 0]);
      cost_pop.append(0);

    pop = np.asarray(pop, np.float64);
    cost_pop = np.asarray(cost_pop, np.float64);

    for i in range(nPop):
      # Initialize Position
      # pop[i] = np.asarray([0.4, 0.6], np.float64)
      pop[i] = np.random.uniform(VarMin[0], VarMax[0], nVar);
      # if(i==0):
      #   pop[i] = np.asarray([0, 1], np.float64)
      # elif (i==1):
      #   pop[i] = np.asarray([1, 0], np.float64)
      # elif (i == 2):
      #   pop[i] = np.asarray([0.5, 0.5], np.float64)
      # Evaluation
      cost_pop[i] = self.CostFunction(pop[i]);

    # Sort Population
    SortOrder = np.argsort(cost_pop);
    cost_pop = cost_pop[SortOrder]
    pop = pop[SortOrder, :];

    # Store Best Solution
    BestSol = pop[0, :];

    # Array to Hold Best Cost Values
    BestCost = np.zeros((MaxIt, 1));

    # Store Cost
    WorstCost = cost_pop[-1];

    # Array to Hold Number of Function Evaluations
    nfe = np.zeros((MaxIt, 1));

    # Main Loop
    for it in range(MaxIt):
      # Calculate Selection Probabilities
      P = np.exp(-1 * beta * cost_pop / WorstCost);
      P = P / np.sum(P);

      # Crossover
      popc1 = [];
      popc2 = [];
      cost_popc1 = [];
      cost_popc2 = [];
      for i in range(int(nc / 2)):
        popc1.append([0, 0]);
        popc2.append([0, 0]);
        cost_popc1.append(0);
        cost_popc2.append(0);

      popc1 = np.asarray(popc1, np.float64);
      popc2 = np.asarray(popc2, np.float64);
      cost_popc1 = np.asarray(cost_popc1, np.float64);
      cost_popc2 = np.asarray(cost_popc2, np.float64);

      for k in range(int(nc / 2)):
        # Select Parents Indices
        i1 = self.RouletteWheelSelection(P);
        i2 = self.RouletteWheelSelection(P);

        # Select Parents
        p1 = pop[i1].copy();
        p2 = pop[i2].copy();

        # Apply Crossover
        [popc1[k], popc2[k]] = self.Crossover(p1, p2, gamma, VarMin, VarMax);

        # Evaluate Offsprings
        cost_popc1[k] = self.CostFunction(popc1[k]);
        cost_popc2[k] = self.CostFunction(popc2[k]);

      popc = np.concatenate((popc1, popc2), 0);
      cost_popc = np.concatenate((cost_popc1, cost_popc2), 0);

      # Mutation
      popm = [];
      cost_popm = [];
      for i in range(int(nm)):
        popm.append([0, 0]);
        cost_popm.append(0);

      popm = np.asarray(popm, np.float64);
      cost_popm = np.asarray(cost_popm, np.float64);

      for k in range(int(nm)):
        # Select Parent
        i = np.random.randint(0, nPop);
        p = pop[i].copy();

        # Apply Mutation
        popm[k] = self.Mutate(p, mu, VarMin[0], VarMax[0]);

        # Evaluate Mutant
        cost_popm[k] = self.CostFunction(popm[k]);

      # Create Merged Population
      pop = np.concatenate((pop, popc), 0);
      cost_pop = np.concatenate((cost_pop, cost_popc), 0);

      pop = np.concatenate((pop, popm), 0);
      cost_pop = np.concatenate((cost_pop, cost_popm), 0);

      # Sort Population
      SortOrder = np.argsort(cost_pop);
      cost_pop = cost_pop[SortOrder];
      pop = pop[SortOrder, :];

      # Truncation
      pop = pop[0:nPop, :];
      cost_pop = cost_pop[0:nPop];

      # Store Best Solution Ever Found
      BestSol = pop[0, :];

      # Store Best Cost Ever Found
      BestCost[it] = cost_pop[0];

      WorstCost = cost_pop[-1];

      nfe[it] = self.NFE;

      print "-----begin------", it
      print "BestSol: ", BestSol;
      print "BestCost: ", BestCost[it];
      print "WorstSol: ", pop[-1];
      print "WorstCost: ", WorstCost;
      print "-----end------", it




def launch (transparent=False):
  initializeSDN()
  ga = GA();
  t = threading.Thread(target=ga.runGA)
  t.daemon = True
  t.start()
  core.registerNew(l2_learning, str_to_bool(transparent))
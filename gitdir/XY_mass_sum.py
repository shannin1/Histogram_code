import numpy as np
from lhereader import LHEReader
import ROOT
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplhep as hep
#from root_numpy import hist2array


ROOT.gROOT.SetBatch(True)

def MakeHistos(proc, vals):

  lhef = os.path.join(os.getcwd(), vals['fin'])
  fout = vals['fin'].split("/")[-1].replace('lhe', 'root')

  fout = ROOT.TFile(fout, 'update')
  fout.cd()

  h_myh     = ROOT.TH1D('h_myh_{0}'.format(proc), ';m(#gamma, h) [GeV];Events;',100, 1399.99, 1400.01)
  h_ctheta  = ROOT.TH1D('h_ctheta_{0}'.format(proc), ';cos(#theta);Events;',40, -1, 1)

  reader = LHEReader(lhef)
  
  for iev, event in enumerate(reader):


     # bs = list(filter(lambda x: abs(x.pdgid)== 5, event.particles))
      print('events: ',event.particles)
      
      hs = list(filter(lambda x: abs(x.pdgid)== 25, event.particles))
      ys = list(filter(lambda x: abs(x.pdgid)== 35, event.particles))
      
      if(len(hs)!=1 or len(ys)!=1):
        print("WARNING: More than one H/y in event")

      
      h_myh.Fill((hs[0].p4() + ys[0].p4()).mass )
      h_p    = np.sqrt(hs[0].energy**2-hs[0].mass**2)
      ctheta = hs[0].pz/h_p

      h_ctheta.Fill(ctheta)

  fout.Write()
  fout.Close()

def MakePlot(procs,log=True,ofile="test.png"):
  
  f       = ROOT.TFile.Open("cmsgrid_final.root")
  
  histos  = []
  edges   = []
  colors  = []
  labels  = []

  for proc in procs:
    h     = f.Get('h_myh_{0}'.format(proc))
    
    #h.Scale(1./h.Integral())
    #hist, edges_2D = hist2array(h,return_edges=True)
    #edges = edges_2D[0]
    
    #edges = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 1)]
    #edges.append(h.GetXaxis().GetBinUpEdge(h.GetNbinsX()))
    #hist = np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)])

    nbins = h.GetNbinsX()
    edges = [h.GetBinLowEdge(i) for i in range(1, nbins + 2)]  # Include overflow bin
    hist = np.array([h.GetBinContent(i) for i in range(1, nbins + 1)])  # Exclude overflow bin


    print(edges)
    print(hist)

    histos.append(hist)
    colors.append(procs[proc]["color"])
    labels.append(procs[proc]["label"])

  plt.style.use([hep.style.CMS])
  f, ax   = plt.subplots()
  plt.sca(ax)
  hep.histplot(histos,edges,stack=False,ax=ax,label=labels,linewidth=2,histtype="step",edgecolor=colors)
  if(log):
    ax.set_yscale("log")
    ax.set_ylim([0.01,10**0])
  else:
    ax.set_ylim([0.,30])
  ax.set_xlim([1399.99, 1400.01])
  plt.xlabel("$m_{H,Y}$",horizontalalignment='left', x=1.0)
  plt.ylabel("Events / bin A.U."  ,horizontalalignment='right', y=1.0)

  hep.cms.lumitext(text="(13 TeV)", ax=ax)
  plt.legend(loc="best")
  
  plt.tight_layout()
  print(ofile)
  plt.savefig(ofile)
  plt.show()

def main():

  procs = {
      'HZy': {
        'fin': "cmsgrid_final.lhe",
        'color':"red",
        'label':"HY"
        },

      #'Hyy': {
       # 'fin': "Hyy/cmsgrid_final.lhe",
        #'color':"darkgreen",
        #'label':"JHUGen H$\gamma\gamma$"
     #   },
      #'SM_LO': {
       # 'fin': "SM_LO/cmsgrid_final.lhe",
        #'color':"blue",
        #'label':"MadGraph LO"
        #},

      }

  for proc, vals in procs.items():
    MakeHistos(proc, vals)

  #MakePlot(procs,log=True,ofile="myh_log.png")
  MakePlot(procs,log=False,ofile="myh_lin.png")
  #cwd = os.getcwd()
  #print("Current working directory:", cwd)

if __name__ == "__main__":
  main()

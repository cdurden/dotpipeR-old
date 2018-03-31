library(workflow)
workflow = new("workflow")
attr(workflow,"name") = "dad-ews-rms_gds971"
attr(workflow,"role") = "mom"
attr(workflow,"experiment_id") = 4
attr(workflow,"investigator") = "Christopher Durden"
attr(workflow,"description") = ""

geo_accession = "GSE967"
for (i in 1:1) {
  workflow = addWorkflowNode(
    workflow,
    data=runComponent("geo0/loadGEOData.R",workflow,name=paste("rawcomponents",i,sep="")) # load raw data
  )
}

workflow = addWorkflowNode(
  workflow,
  data=runComponent("loading/annotateAssayData.R",workflow,parents="rawcomponents1", name="rawdata1") # load raw data
)
arraydata = workflow['rawdata1']$arraydata
ews = targets(arraydata)[,"description"][1]
is_ews = (targets(arraydata)[,"description"] == ews)
ews_means = rowMeans(assaydata(arraydata)[,targets(arraydata)[,"description"] == ews])
rms_means = rowMeans(assaydata(arraydata)[,targets(arraydata)[,"description"] != ews])
#delta = diabetes_means-ews_means
#h19 = which(levels(probes(arraydata)[,12])[probes(arraydata)[,12]]==283120)
#h19 = grep("283120",probes(arraydata)[,12])
h19 = grep("ASM",probes(arraydata)[,11])
#grep("ASM1",probes(arraydata)[,11])
#grep("BWS",probes(arraydata)[,11])
#grep("D11S813E",probes(arraydata)[,11])
#grep("MGC4485",probes(arraydata)[,11])
#grep("NCRNA00008",probes(arraydata)[,11])
#grep("PRO2605",probes(arraydata)[,11])
#igf1 = grep("IGF1",probes(arraydata)[,11])
igf1 = which(levels(probes(arraydata)[,11])[probes(arraydata)[,11]]=="IGF1")
probes(arraydata)[igf1,11]
probes(arraydata)[h19,11]
#png("/var/www/sites/cld/cld/public/files/tmp/igf1_diabetes.png")
#plot(colMeans(assaydata(arraydata)[igf1,])~as.numeric(is_ews))
#dev.off()

#imprinted_genes = read.delim("~/svn/cld/projects/imprinted_genes/imprinted_genes.txt",sep="\t")[,1]

#map = list()
#for (gene in imprinted_genes) {
#  rows = which(probes(workflow['rawdata1']$arraydata)[,11]==gene)
#  map[[gene]] = rows
#}

rm(arraydata)

workflow = addWorkflowNode(
  workflow,
  data=runComponent("log.R",workflow,parents=c("rawdata1"),name="logdata")) # load raw data

design = cbind(rep(1,length(is_ews)), as.numeric(is_ews))
colnames(design) = c("intercept","ews")

workflow = addWorkflowNode(
  workflow,
  data=runComponent("ols.R",workflow,parents=c("logdata"),name="lm_ews")) # load raw data


rm(design)

workflow = addWorkflowNode(
  workflow,
  data=runComponent("stats.R",workflow,parents=c("lm_ews"),name="ews_statistics")) # load raw data


i=11
workflow = addWorkflowNode(
  workflow,
  data=runComponent("annotation/annotateStatsByArraydata.R",workflow,parents=c("ews_statistics","rawdata1"),name="ews_statistics_annotated")) # load raw data


workflow

#Owen Galvin
#E63 Big Data Analytics
#Assignment 01, R code for three problem sets


#Problem 1
V = c(7,2,1,0,3,-1,-3,4)
A = matrix(data=V, nrow=4)
A
AT = t(A)
AT
A %*% AT
AT %*% A
solve(A %*% AT)
solve(AT %*% A)
V = c(V,-2)
V
B = matrix(data=V, nrow=3)
B
Binv = solve(B)
Binv
b1 = B %*% Binv
b2 = Binv %*% B
b1 == b2
b1
b2
isTRUE(all.equal(b1,b2))
identical(b1,b2)
apply(b1, 1:2, round, digits=10)
apply(b2, 1:2, round, digits=10)
#Determine the eigenvectors of matrixes B.
eigB = eigen(B)
eigB
eigB$vectors  # the eigen vectors
C = eigB$vectors
C
C %*% B
B %*% C
eigB$values * eigB$vectors
dimnames(B) = list(c('R1','R2','R3'), c('C1','C2','C3'))
dfB = as.data.frame(B)
dfB
class(dfB)


#Problem 2
power = read.csv('2006Data.csv')
plot(power$Power, power$Temperature)
plot(power$Power, power$Hour)
boxplot(Power ~ Hour, data=power, xlab='Hour of Day', ylab='Power Consumption')


#Problem 3
power = read.csv('2006Data.csv')
power$temperatureBin = cut(power$Temperature, breaks=50, right=FALSE)
binPowerAvgs = tapply(power$Power, power$temperatureBin, mean)
power$binAvgPower = binPowerAvgs[power$temperatureBin]
binPowerMins = tapply(power$Power, power$temperatureBin, min)
power$binMinPower = binPowerMins[power$temperatureBin]
binPowerMaxs = tapply(power$Power, power$temperatureBin, max)
power$binMaxPower = binPowerMaxs[power$temperatureBin]
binMedianTemperatures = tapply(power$Temperature, power$temperatureBin, median)
power$binMedianTemperature = binMedianTemperatures[power$temperatureBin]
dfBins = as.data.frame(unique(cbind(power$binMedianTemperature, power$binAvgPower, power$binMinPower, power$binMaxPower)))
colnames(dfBins) = c('medTemperature','avgPower','minPower','maxPower')
nrow(dfBins)

min(power$Power); max(power$Power);
yrange=c(30,105)
plot(cbind(dfBins$medTemperature, dfBins$avgPower), pch=19, col='red', xlab='Temperature', ylab='Power Consumption', ylim=yrange)
par(new=TRUE)
plot(cbind(dfBins$medTemperature, dfBins$minPower), pch=0, col='blue', xlab='', ylab='', ylim=yrange)
par(new=TRUE)
plot(cbind(dfBins$medTemperature, dfBins$maxPower), pch=17, col='green', xlab='', ylab='', ylim=yrange)
legend(70,108, c('Maximum','Average','Minimum'), col=c('green','red','blue'), pch=c(17,19,0), cex=0.7, bty='n')

cov(cbind(dfBins$medTemperature, dfBins$avgPower))
cov(cbind(dfBins$medTemperature, dfBins$minPower))
cov(cbind(dfBins$medTemperature, dfBins$maxPower))


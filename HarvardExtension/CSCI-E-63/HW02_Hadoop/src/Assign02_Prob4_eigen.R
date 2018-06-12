A = matrix(data=c(3,2,4,2,0,2,4,2,3), ncol=3)
A
eigen(A)
eigA = eigen(A)$vectors
eigA

#mutually orthogonal
ortho = eigA[,1] %*% eigA[,2] %*% eigA[,2]
ortho
round(ortho, digits=10)
#alternate?
x = eigA[,1]
y = eigA[,2]
z = eigA[,3]
round(t(x) %*% y)
round(t(y) %*% z)
round(t(z) %*% x)

eigA.t = t(eigA)
eigA.t
product = eigA.t %*% A %*% eigA
product
apply(product, 1:2, round, digits=10)


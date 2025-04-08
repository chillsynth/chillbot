FROM golang:1.24-alpine as build

WORKDIR /usr/src/app

COPY go.mod go.sum ./
RUN go mod download && go mod verify
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64

COPY . .

# RUN go build -ldflags "-w -s" ./cmd/gocamp
RUN go build -ldflags "-w -s" -v -o /usr/local/bin/chillbot .

FROM scratch

# EXPOSE 8080

WORKDIR /app

COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /usr/local/bin/chillbot /app/chillbot
COPY ./config/ /app/config/

CMD ["/app/chillbot"]
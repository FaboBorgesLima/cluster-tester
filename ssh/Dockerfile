FROM debian:12-slim

# install ssh

RUN apt-get update && apt-get install -y \
    openssh-server sysstat 

EXPOSE 22


RUN echo 'root:root' | chpasswd
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

RUN service ssh restart

CMD ["/usr/sbin/sshd", "-D"]
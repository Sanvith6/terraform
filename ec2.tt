# Key pair for EC2 instance
resource "aws_key_pair" "my_key_pair" {
  key_name   = "terra-key-ec2"
  public_key = file("terra-key-ec2.pub")
}

# Default VPC
resource "aws_default_vpc" "my_default_vpc" {}

# Security Group
resource "aws_security_group" "my_security_group" {
  name        = "allow_ssh_http"
  description = "Security group to allow SSH and app traffic"
  vpc_id      = aws_default_vpc.my_default_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow SSH"
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow app traffic"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "my_ec2_instance" {
  ami                    = var.ec2_ami_id # Ubuntu (region-specific!)
  instance_type          = var.ec2_instance_type
  key_name               = aws_key_pair.my_key_pair.key_name
  vpc_security_group_ids = [aws_security_group.my_security_group.id]

  root_block_device {
    volume_size = var.ec2_root_storage_size
    volume_type = "gp3"
  }

  tags = {
    Name = "MyEC2Instance"
  }
}

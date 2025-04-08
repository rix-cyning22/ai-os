Code to generate a docker image of AI-optimised OS.

# Functionalities:
1. The OS comes pre-installed with CUDA for NVIDIA GPU support, miniconda for version management and virtual environment creation, pytorch and tensorflow.
2. A smart scheduling algorithm has been built that can schedule processes using an ML algorithm
3. A smart anomaly detection algorithm that can flag anomalous processes that consume too much memory or takes too long to execute.
4. A CLI-based resource monitoring program
5. GUI support for resource monitoring program. A dashboard visualises the resources being used
6. a script to automate virtual environment set up using conda
7. An installation script (ONLY USE IT IF DOCKER IS NOT ALREADY INSTALLED!!)
8. GPU memory management scripts

After installing docker, the docker image can be built using the following command:
```
    sudo docker build -t <image_name> .    
```
The docker image can be run using
```
    sudo docker run -it <image_name>
```

Due to space constrainsts in github, the final iso image could not be uploaded. However, the iso image can be generated using:

## 🛠️ Building a Bootable ISO from a Docker Image

This guide explains how to convert a Docker image of a Linux-based operating system into a **bootable ISO image** using GRUB and SquashFS.

---

## 📦 Prerequisites

Ensure you have the following installed:

- Docker
- `mksquashfs` (from `squashfs-tools`)
- `grub-mkrescue`
- `xorriso`
- `qemu-system-x86` (for optional testing)

Install required tools (on Ubuntu):
```
sudo apt install grub-pc-bin grub-common grub-efi-amd64-bin grub-mkrescue xorriso squashfs-tools qemu-system-x8
```
Steps to Build the ISO
1. Export Docker Image

Export the root filesystem of the Docker image:

docker export $(docker create my-os-image) | tar -x -C rootfs/

This extracts the container's root filesystem into a local rootfs/ directory.
2. Create SquashFS from Root Filesystem

mksquashfs rootfs/ filesystem.squashfs -e boot

This compresses the root filesystem (excluding the /boot directory) into a read-only image.
3. Prepare the Boot Directory

Copy kernel and initramfs from the extracted rootfs:

mkdir -p iso/boot
cp rootfs/boot/vmlinuz iso/boot/
cp rootfs/boot/initrd.img iso/boot/

4. Create GRUB Configuration

mkdir -p iso/boot/grub

Create the grub.cfg file:

# iso/boot/grub/grub.cfg
menuentry "My OS" {
    linux /boot/vmlinuz boot=casper quiet splash ---
    initrd /boot/initrd.img
}

5. Add SquashFS Image

mkdir -p iso/casper
mv filesystem.squashfs iso/casper/

6. Create the Bootable ISO

grub-mkrescue -o myos.iso iso/

This builds the ISO with GRUB as the bootloader.
🧪 Testing with QEMU (Optional)

Boot and test your ISO:

qemu-system-x86_64 -cdrom myos.iso -m 2048

📝 Notes

    The bootloader uses GRUB in BIOS mode by default.

    You can use UEFI by providing OVMF_CODE.fd and configuring accordingly.

    Ensure initrd.img and vmlinuz are compatible with the rest of the rootfs.

    If you see "No init found" errors, check that your extracted rootfs includes /sbin/init or equivalent.

📁 Directory Structure

iso/
├── boot/
│   ├── grub/
│   │   └── grub.cfg
│   ├── vmlinuz
│   └── initrd.img
└── casper/
    └── filesystem.squashfs


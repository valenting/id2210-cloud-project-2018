%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LaTeX Example: Project Report
%
% Source: http://www.howtotex.com
%
% Feel free to distribute this example, but please keep the referral
% to howtotex.com
% Date: March 2011 

%\title{Project Report}
%
%%% Preamble
\documentclass[paper=a4, fontsize=11pt]{scrartcl}
\usepackage[T1]{fontenc}
\usepackage{fourier}

\usepackage[english]{babel}                             % English language/hyphenation
\usepackage[protrusion=true,expansion=true]{microtype}  
\usepackage{amsmath,amsfonts,amsthm} % Math packages
\usepackage[pdftex]{graphicx} 
\usepackage{url}
\usepackage{hyperref}

\usepackage{minted}
\usepackage{multirow}

%%% Custom sectioning
\usepackage{sectsty}
\allsectionsfont{\centering \normalfont\scshape}


%%% Custom headers/footers (fancyhdr package)
\usepackage{fancyhdr}
\pagestyle{fancyplain}
\fancyhead{}                      % No page header
\fancyfoot[L]{}                     % Empty 
\fancyfoot[C]{}                     % Empty
\fancyfoot[R]{\thepage}                 % Pagenumbering
\renewcommand{\headrulewidth}{0pt}      % Remove header underlines
\renewcommand{\footrulewidth}{0pt}        % Remove footer underlines
\setlength{\headheight}{13.6pt}


%%% Equation and float numbering
\numberwithin{equation}{section}    % Equationnumbering: section.eq#
\numberwithin{figure}{section}      % Figurenumbering: section.fig#
\numberwithin{table}{section}       % Tablenumbering: section.tab#


%%% Maketitle metadata
\newcommand{\horrule}[1]{\rule{\linewidth}{#1}}   % Horizontal rule

\title{
    %\vspace{-1in}  
    \usefont{OT1}{bch}{b}{n}
    \normalfont \normalsize \textsc{ID2210 VT18-1 Distributed Computing, Peer-to-Peer and GRIDS} \\ [25pt]
    \horrule{0.5pt} \\[0.4cm]
    \huge Working with the cloud - Project report \\
    \horrule{2pt} \\[0.5cm]
}
\author{
    \normalfont                 \normalsize
        Valentin Gosu\\[-3pt]   \normalsize
        \href{mailto:gosu@kth.se}{gosu@kth.se} \\[-3pt]   \normalsize
        \today
}
\date{}

%%% Begin document
\begin{document}
\maketitle
\section{Task 1 - External storage support}
\subsection{Task 1.1 - Storage types}

% https://cloud.google.com/storage/docs/storage-classes

Google Cloud Platform currently provides four storage types when creating a bucket:
\begin{itemize}
  \item \textbf{Multi-regional} - has the best availability and redundancy. It's supposed to be used for serving frequently accessed files to clients around the world.
  \item \textbf{Regional} - has high availability and redundancy, and is supposed to be used mainly by applications running in Google Compute Engine in the same  region.
    \item \textbf{Nearline} - is dedicated for data that is rarely accessed, such as backups or really unpopular media files.
    \item \textbf{Coldline} - is for data that is rarely, if ever, accessed. This is for data that is archived for historical purposes or disaster recovery.
\end{itemize}

For the purposes of this project, I only used \textit{regional} and \textit{multi-regional} buckets. The benchmark includes 5 testcases, with 3 regional buckets, and 2 multi-regional buckets being accessed from my home computer.

\subsection{Task 1.2 - Reading and writing to the storage}

I implemented all tasks in Python, for reasons including the flexibility of the programming language, availability of an API to access the Google cloud resources, and my own familiarity with it.

By reading the docs, I came across the library called \textit{google-cloud-storage}. This library provides an high-level abstraction layer for the storage buckets and hides the HTTP transfer protocol being used to interact with the buckets.

While it is possible to both push a file to the storage and stream content to the bucket, I chose to only deal with files.

Alternatives APIs also exist, in other programming languages, likely all based on the same REST API. For the purposes of checking my code I also used the \textit{gsutil} tool to verify that the files were actually uploaded and were correct.

Note: In the associated code, most of the reusable code is implemented in \textit{functions.py}, while tasks are performed in separate python files. In order to reproduce the results, one needs to add a \textit{service\_account\_credentials.json} file containing the downloaded credentials, or to specify it via the \textit{GOOGLE\_APPLICATION\_CREDENTIALS} environment variable.
Also, the \textit{PROJECT} and \textit{USER} variables in \textit{functions.py} should be updated to match those in the provided credentials.

\subsection{Task 1.3 - Storage performance}

\begin{table}[htb]
\centering
\caption{Bandwidth to bucket from local PC}
\begin{tabular}{|l|l|l|l|}
\hline
Bucket Name                                           & Thread count & Write bw (MBps) & Read bw (MBps) \\ \hline
\multirow{3}{*}{australia-southeast1-regional}        & 1 & 1.12 & 4.12         \\ \cline{2-4} 
                                                      & 2 & 1.14 & 4.78         \\ \cline{2-4} 
                                                      & 4 & 1.14 & 5.42         \\ \hline
\multirow{3}{*}{eu-multi\_regional}                    & 1 & 1.14 & 5.61         \\ \cline{2-4} 
                                                      & 2 & 1.14 & 5.66         \\ \cline{2-4} 
                                                      & 4 & 1.14 & 5.73         \\ \hline
\multirow{3}{*}{europe-west1-regional}                & 1 & 1.14 & 5.52        \\ \cline{2-4} 
                                                      & 2 & 1.14 & 5.67        \\ \cline{2-4} 
                                                      & 4 & 1.15 & 5.72         \\ \hline
\multirow{3}{*}{us-east1-regional}                    & 1 & 1.14 & 5.25         \\ \cline{2-4} 
                                                      & 2 & 1.14 & 5.54        \\ \cline{2-4} 
                                                      & 4 & 1.14 & 5.65         \\ \hline
\multirow{3}{*}{us-multi\_regional}                    & 1 & 1.12 & 5.41         \\ \cline{2-4} 
                                                      & 2 & 1.14 & 5.25         \\ \cline{2-4} 
                                                      & 4 & 1.14 & 5.55         \\ \hline
\end{tabular}
\end{table}

As we can see the transfers quickly saturate the bandwidth provided by my ISP, so there isn't much we can say about the buckets by looking at the table.

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_storage.py}{Link to code}

\section{Task 2 - Setting up a VM}

\subsection{Task 2.1 - Web Console}

Setting up the VM via the web consoles is a fairly easy task.
All one needs to do is to go to the web page located at \textbf{https://console.cloud.google.com/compute/instances?project=[PROJECT]},
and click the \textit{Create} button.

Then one needs to fill out the form with various information describing the VM such as \textit{name}, \textit{zone}, \textit{machine type} and various other properties that are initially hidden:  \textit{extra disks}, \textit{startup script}, \textit{metadata}, \textit{SSH keys}, etc.

Finishing this process and clicking the \textit{Create} button will create and start the VM (provided that all configuration options are correct).
What makes the web console very useful is that the page also features couple links at the bottom entitled \textit{REST} and \textit{command line}. Clicking them will open a pop-up containing the configuration options in either JSON or command line command form.
This makes the automation of operations very easy, as all you have to do is to transfer the options to your code.

\subsection{Task 2.2 - API for VM creation}

The Python API I used for creating and deleting VMs is \textbf{google-api-python-client}.
This API is less high level than the storage API library, probably because it needs to have a high degree of control over all the properties of the VM.
Another peculiarity of the API is that VM names are not unique, and as such we always need to provide the zone in which the VM is running to be able to identify it.
While for most tasks the VMs were located in the same zone, this became an issue in task 4.2, where VMs in multiple zones had to be started and shutdown. As an easy fix, I implemented a separate method that listed the VMs in all available zones, and shut down all of them.
I got the list of zones by running \textbf{gcloud compute zones list}, and hardcoded the list of zones within my app. Ideally, the list of zones should be generated at runtime.

In order to complete the other tasks, I needed a way to run commands inside the VMs. In order to do so I chose to use SSH via the \textbf{paramiko} library. Before creating the VMs I generate an SSH key, which I pass to the VM on creation.
This allows me to create an SSH session, which then is used to run a command or upload a file to the VM.

\subsection{Task 2.3 - VM connectivity via TCP/UDP}

The connectivity check uses the \textbf{nc} command on the VM, while locally I just create sockets using the Python API and connect to the external IP of that VM.

One important step I had to take was setting up the firewall rule to allow incoming traffic to the VM on arbitrary port 2222. This rule is per-project, so for the rest of the experiment we only used port 2222 to perform our network tests.

\begin{minted}{bash}
gcloud compute --project=id2210-vt18-group3 firewall-rules create fw-2222
   --direction=INGRESS --priority=1000
   --network=default --action=ALLOW
   --rules=tcp:2222,udp:2222 --source-ranges=0.0.0.0/0
\end{minted}

Upon connecting, sending data via the socket and closing the socket, we then check that the data was received on the VM. 

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_compute.py}{Link to code}

\section{Task 3 - Internal storage support}

\subsection{Task 3.1 - Mounting external storage}

% https://cloud.google.com/compute/docs/disks/gcs-buckets
% https://cloud.google.com/storage/docs/gcs-fuse
Mounting buckets on VMs is done via the gcs-fuse tool. One issue I had is that this tool does not come preinstalled on the VM images, so I had to change the startup script to install it via \textit{apt-get}.
The tool creates and mounts a virtual filesystem. Each operation on the filesystem corresponds to one or more HTTP operations that may be performed as a consequence.

One important characteristic of the GCS buckets is that they are non-hierarchical, which means that folders aren't an entity that is represented in GCS; however files can be prefixed by a string that looks like a folder path, and the FUSE system will display as a being a folder.

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/startup_script.sh}{Link to code}

\subsection{Task 3.2 - External storage access}

For the purposes of this task I crated two files \textit{generate\_file.py} and \textit{read\_file.py}. They both take a filepath as an argument, and either generate a file or read that file. The generated file is not random, but composed of incremental bytes blocks, with a total size of 100MB.

For this task, I used the same buckets as in Task 1.3, and a VM located in "us-east1".
I then mounted the buckets, and used the helper files to generate and read back the generated files. These operations were performed 5 times, and then reported an average transfer speed.

As we can see, location does have an effect on the speed. It is unclear however if the bucket type has any effect on the bandwidth, other than having a better bandwidth for multi-regional bucket because we're connecting to the one closest to us. The fact that we're reading the file that we just uploaded is probably not able to benefit from the replication of data in multi-regional buckets.

\begin{table}[htb]
\centering
\caption{Bandwith to mounted storage}
\begin{tabular}{|l|l|l|l|}
\hline
Bucket Name                                           & Thread count & Write bw (MBps) & Read bw (MBps) \\ \hline
\multirow{3}{*}{australia-southeast1-regional}        & 1            & 8.90           &  110.47         \\ \cline{2-4} 
                                                      & 2            & 14.33          &  141.83         \\ \cline{2-4} 
                                                      & 4            & 17.92          &  154.60         \\ \hline
\multirow{3}{*}{eu-multi\_regional}                    & 1            & 13.80          &  130.63         \\ \cline{2-4} 
                                                      & 2            & 18.28          &  169.43         \\ \cline{2-4} 
                                                      & 4            & 16.79          &  222.86         \\ \hline
\multirow{3}{*}{europe-west1-regional}                & 1            & 5.73           & 129.49         \\ \cline{2-4} 
                                                      & 2            & 5.29           & 176.59         \\ \cline{2-4} 
                                                      & 4            & 11.17           & 214.99         \\ \hline
\multirow{3}{*}{us-east1-regional}                    & 1            & 11.65           & 168.42         \\ \cline{2-4} 
                                                      & 2            & 8.50           & 251.86         \\ \cline{2-4} 
                                                      & 4            & 19.85           & 379.84         \\ \hline
\multirow{3}{*}{us-multi\_regional}                    & 1            & 10.31           & 146.34         \\ \cline{2-4} 
                                                      & 2            & 16.65           & 213.05         \\ \cline{2-4} 
                                                      & 4            & 19.72           & 339.73         \\ \hline
\end{tabular}
\end{table}

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_internal_storage.py}{Link to code}

\subsection{Task 3.3 - VM local storage access}

Similar to the previous task, I performed the same task for the local file system (both HDD and SDD).
One obstacle that I hit was that initially I was using "micro" instances to perform my testing. However, these instances are not allowed to add and SSD, so the operation would fail with a cryptic message.

% Write speed (bucket: . parralel_count:1): 41.17 MBps
% Read speed (bucket: . parralel_count:1): 190.04 MBps
% Write speed (bucket: . parralel_count:2): 36.78 MBps
% Read speed (bucket: . parralel_count:2): 362.07 MBps
% Write speed (bucket: . parralel_count:4): 35.78 MBps
% Read speed (bucket: . parralel_count:4): 470.71 MBps

\begin{table}[htb]
\centering
\caption{HDD bandwidth}
\begin{tabular}{|l|l|l|}
\hline
Thread count & Write bw (MBps) & Read bw (MBps) \\ \hline
1            & 190.04          & 41.17          \\ \hline
2            & 362.07          & 36.78          \\ \hline
4            & 470.71          & 35.78          \\ \hline
\end{tabular}
\end{table}

\begin{table}[htb]
\centering
\caption{SSD bandwidth}
\begin{tabular}{|l|l|l|}
\hline
Thread count & Write bw (MBps) & Read bw (MBps) \\ \hline
1            & 149.60          & 221.60          \\ \hline
2            & 291.65          & 422.66          \\ \hline
4            & 395.57          & 661.50          \\ \hline
\end{tabular}
\end{table}

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_internal_storage.py#L63-L73}{Link to code}

% Write speed (bucket: ssd parralel_count:1): 149.60 MBps
% Read speed (bucket: ssd parralel_count:1): 221.60 MBps
% Write speed (bucket: ssd parralel_count:2): 291.65 MBps
% Read speed (bucket: ssd parralel_count:2): 422.66 MBps
% Write speed (bucket: ssd parralel_count:4): 395.57 MBps
% Read speed (bucket: ssd parralel_count:4): 661.50 MBps

\section{Task 4 - Simple Network}
\subsection{Task 4.1 - TCP/UDP benchmark}

For this task I used the \textbf{iperf} tool.
As an endpoint, I created a VM in the "us-east1-b" zone.
After running the iperf client, we look at the results on the server to get an accurate report of the bandwidth.

\begin{table}[htb]
\centering
\caption{PC to VM network bandwidth (Mbits/sec)}
\begin{tabular}{|l|l|l|}
\hline
VM zone & TCP & UDP \\ \hline
us-east1-b            & 8.62          & 9.69          \\ \hline
\end{tabular}
\end{table}

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_iperf.py}{Link to code}

\subsection{Task 4.2 - VM to VM network benchmark}

I also used iperf to benchmark VM to VM network communication.
The test is performed from each of the zones to one server VM located in "us-east1-b"

\begin{table}[htb]
\centering
\caption{Transfer bandwidth (Mbits/sec)}
\begin{tabular}{|l|l|l|}
\hline
ZONE & TCP & UDP \\ \hline
us-east1-b & 1090 & 715\\ \hline
us-east1-c & 1220 &  685   \\ \hline
us-east4-a & 1030 &  693   \\ \hline
europe-west4-a & 225 &  769   \\ \hline
australia-southeast1-b & 97 &  716   \\ \hline
\end{tabular}
\end{table}

As we can see for TCP, locality is very important, as the bandwidth drops are obviously related to the distance from the server.
However, UDP appears to be rate limited to under 800 Mbits/second, but for large distances it is able to achieve a higher bandwidth at the expense of packet loss and out-of-order packet arrivals, which may be OK for some applications.

\href{https://github.com/valenting/id2210-cloud-project-2018/blob/master/test_network.py}{Link to code}

%%% End document
\end{document}
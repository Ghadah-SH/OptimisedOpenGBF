// system_metrics.c
#include "system_metrics.h"
#include <stdio.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <stdlib.h>


//Function to Get CPU Utilization:This function reads the CPU times at two different instances (with a second apart) and calculates the percentage of CPU utilization during that time.

double get_cpu_usage() {
     static long double last_total = 0, last_idle = 0;
    long double a[4], total, loadavg;
    FILE *fp;
    fp = fopen("/proc/stat","r");
    if (!fp){
    perror("Failed to open /proc/stat");
    return -1; // Inidicate failure
    }
    
    if(fscanf(fp, "%*s %Lf %Lf %Lf %Lf", &a[0], &a[1], &a[2], &a[3]) !=4) {
    perror("Failed to read CPU stat");
    fclose(fp);
    return -1; // Inidicate failure 
    }
   
    fclose(fp);

    total = a[0] + a[1] + a[2] + a[3];
    loadavg = last_idle == 0 ? 0 : ((a[2] - last_idle) / (total - last_total));
    last_total = total;
    last_idle = a[2];

    return (1.0 - loadavg) * 100.0;
}


//Function to Get Memory Usage:This function reads the total and free memory values and calculates the percentage of used memory.

double get_memory_usage() {
    long long total_memory=0 , free_memory=0;
    FILE *fp = fopen("/proc/meminfo", "r");
    if(!fp) {
    perror("Failed to open /proc/meminfo");
    return -1; // Indicate failure
    }
    
     
    if(fscanf(fp, "MemTotal: %lld kB\nMemFree: %lld kB", &total_memory, &free_memory) !=2 ){
    perror("Failed to read memory info");
    fclose(fp);
    return -1; // Inidicate failure 
    
    }
    fclose(fp);
    return 100.0 * (total_memory - free_memory) / total_memory;
}


//Function to Get Thread Count:This function counts the number of directories in /proc/self/task, which corresponds to the number of threads in the current process.

int get_thread_count() {
    int count = 0;
    DIR *dir;
    dir = opendir("/proc/self/task");
    if (dir == NULL) {
    perror("Failed to open directory /proc/self/task");
    return -1; // Return an error 
    
    }
    
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_DIR) {
            ++count;
        }
    }

    closedir(dir);
    return count - 2; // Subtract 2 for "." and ".." directories
}




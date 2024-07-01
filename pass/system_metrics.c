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
    fscanf(fp, "%*s %Lf %Lf %Lf %Lf", &a[0], &a[1], &a[2], &a[3]);
    fclose(fp);

    total = a[0] + a[1] + a[2] + a[3];
    loadavg = last_idle == 0 ? 0 : ((a[2] - last_idle) / (total - last_total));
    last_total = total;
    last_idle = a[2];

    return (1.0 - loadavg) * 100.0;
}


//Function to Get Memory Usage:This function reads the total and free memory values and calculates the percentage of used memory.

double get_memory_usage() {
    long long total_memory, free_memory;
    FILE *fp = fopen("/proc/meminfo", "r");
    fscanf(fp, "MemTotal: %lld kB\nMemFree: %lld kB", &total_memory, &free_memory);
    fclose(fp);

    return 100.0 * (total_memory - free_memory) / total_memory;
}


//Function to Get Thread Count:This function counts the number of directories in /proc/self/task, which corresponds to the number of threads in the current process.

int get_thread_count() {
    int count = 0;
    DIR *dir;
    struct dirent *entry;

    dir = opendir("/proc/self/task");
    if (dir == NULL) {
        perror("Failed to open directory");
        return -1;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_DIR) {
            ++count;
        }
    }

    closedir(dir);
    return count - 2; // Subtract 2 for "." and ".." directories
}




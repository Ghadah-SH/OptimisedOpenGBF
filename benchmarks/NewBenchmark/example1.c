#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <string.h>
#include <assert.h>
#include "myDelaylib.h" // Include your delay library

void reach_error() { assert(0); }

void __VERIFIER_assert(int expression) {
    if (!expression) { 
        ERROR: {reach_error();abort();};
    }
    return;
}

char *v;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *thread1(void *arg)
{
    pthread_mutex_lock(&lock);
    v = calloc(8, sizeof(char));
    _delay_function(); // Introduce delay
    pthread_mutex_unlock(&lock);
    return 0;
}

void *thread2(void *arg)
{
    _delay_function(); // Introduce delay
    pthread_mutex_lock(&lock);
    if (v) strcpy(v, "Bigshot");
    pthread_mutex_unlock(&lock);
    return 0;
}

int main()
{
    pthread_t t1, t2;

    pthread_create(&t1, 0, thread1, 0);
    pthread_create(&t2, 0, thread2, 0);
    pthread_join(t1, 0);
    pthread_join(t2, 0);

    __VERIFIER_assert(!v || v[0] == 'B');

    return 0;
}


//this file is for Improved_EBF2 with delays. 

extern void abort(void);
#include <assert.h>

void reach_error() { assert(0); }

//void reach_error() { assert(0); }

#include <pthread.h>
#include <assert.h>
#include <unistd.h>

pthread_mutex_t  mutex;
int data = 0;

void *thread1(void *arg)
{
  pthread_mutex_lock(&mutex);
  data++;
  pthread_mutex_unlock(&mutex);
  sleep(2); // Increase sleep time
  return 0;
}


void *thread2(void *arg)
{
  pthread_mutex_lock(&mutex);
  data += 2;
  pthread_mutex_unlock(&mutex);
  sleep(3); // Increase sleep time
  return 0;
}


void *thread3(void *arg)
{
  pthread_mutex_lock(&mutex);
  if (data >= 3){
    ERROR: {reach_error();abort();}
    ;
  }
  pthread_mutex_unlock(&mutex);
  sleep(4); // Increase sleep time
  return 0;
}


void *thread4(void *arg)
{
  pthread_mutex_lock(&mutex);
  data -= 1;
  pthread_mutex_unlock(&mutex);
  sleep(5); // New thread with additional sleep time
  return 0;
}


void *thread5(void *arg)
{
  pthread_mutex_lock(&mutex);
  data += 3;
  pthread_mutex_unlock(&mutex);
  sleep(6); // New thread with additional sleep time
  return 0;
}


int main()
{
  pthread_mutex_init(&mutex, 0);

  pthread_t t1, t2, t3, t4, t5;

  pthread_create(&t1, 0, thread1, 0);
  pthread_create(&t2, 0, thread2, 0);
  pthread_create(&t3, 0, thread3, 0);
  pthread_create(&t4, 0, thread4, 0);
  pthread_create(&t5, 0, thread5, 0);

  pthread_join(t1, 0);
  pthread_join(t2, 0);
  pthread_join(t3, 0);
  pthread_join(t4, 0);
  pthread_join(t5, 0);
  
  return 0;
}


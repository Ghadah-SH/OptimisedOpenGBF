//#include <assert.h> 
#include <stdio.h> 
int main() { 
  char ch; 
  scanf("%c", &ch); 
  
   if (ch == 'A') {
    printf("Error: Input character cannot be 'A'\n");
    return 1; // Exit with a non-zero status to indicate an error
  } 
 // assert(ch != 'A'); 
  return 0; 
} 




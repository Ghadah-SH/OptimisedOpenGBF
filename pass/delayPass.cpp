#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/InitializePasses.h"
#include "llvm/Transforms/Utils/Local.h"
#include "llvm/IR/PassManager.h"
#include "delayPass.hpp"



bool DelayPass::runOnFunction(llvm::Function &F) {
return injectDelays(F);
}

llvm::StringRef DelayPass::getFunctionName(llvm::CallInst *callInst)
{
    llvm::Function *calleeFunction = callInst->getCalledFunction();
    /* if we can't determine the called function, then return false */
    if (calleeFunction == NULL)
    {
        /* we get the function as operand and strip the pointer cast (we get the uncasted value)*/
        llvm::Value *v = callInst->getCalledOperand();
        calleeFunction = llvm::dyn_cast<llvm::Function>(v->stripPointerCasts());
        if (calleeFunction == NULL)
        {
            return "";
        }
    }
    // we should have found the calee function
    assert(calleeFunction != NULL);
    // Get the function name
    return calleeFunction->getName();
}

void DelayPass::initializeEBFFunctions()
{
    llvm::Function &F = *this->currentFunction;
    /*Obtain a function type consisting of void signature.*/
    llvm::FunctionType *voidfunctionTy = llvm::FunctionType::get(llvm::Type::getVoidTy(*this->Ctx), false);
    /* Define the add thread function call and release thread function call.
     * The signature is void add_thread() and  void join_thread() respectively.*/
    this->addF = F.getParent()->getOrInsertFunction("add_thread", voidfunctionTy);
    this->joinF = F.getParent()->getOrInsertFunction("join_thread", voidfunctionTy);
    /* Define the delay function call.
     * The signature is void __delay_function(). */
    this->delayF = F.getParent()->getOrInsertFunction(delayFunction, voidfunctionTy);
}


bool DelayPass::instrumentThreadCounting(llvm::Instruction *I)
{
   llvm::CallInst *callInst = llvm::dyn_cast<llvm::CallInst>(&*I);

    if (callInst != NULL)
    {
        auto functionName = getFunctionName(callInst);
        llvm::errs() << "check functionName\n\n "
                     << functionName;

        /* 1) Try to get function name
           2) if thread creation then insert a call to count active threads function.
           3) if thread release then insert a call to count release threads function */

        if (functionName == "pthread_create")
        {
            llvm::IRBuilder<> builder(I);
            builder.CreateCall(addF);
        }
        if (functionName == "pthread_join")
        {
            llvm::IRBuilder<> builder(I);
            builder.CreateCall(joinF);
        }
    }
    return true;
}


bool DelayPass::shouldInjectDelay(llvm::Instruction *I) {
llvm::CallInst *callInst = llvm::dyn_cast<llvm::CallInst>(I);
if (!callInst) return false; 

llvm::StringRef functionName = getFunctionName(callInst);
if(functionName == "pthread_mutex_lock" || functionName == "pthread_mutex_unlock" || functionName == "pthread_create" || functionName == "pthread_join") {
return true;

}
return false;



}



bool DelayPass::injectDelays(llvm::Function &F)
{
Ctx = &F.getContext();
currentFunction = &F;
initializeEBFFunctions();
bool inserted = false;


    /* iterate for each function and each basicblock */
    for (llvm::Function::iterator bb = F.begin(), e = F.end(); bb != e; ++bb)
    {
        for (llvm::BasicBlock::iterator i = bb->begin(), e = bb->end(); i != e; ++i)
        {
            /* get instruction i*/
            llvm::Instruction *I = &*i;
            /* */
            //Instrument thread counting logic
            instrumentThreadCounting(I);
            if (shouldInjectDelay(I))
            { /* insert a call to the delay function. */
                llvm::IRBuilder<> builder(I);
                
                // Insert a call to the delay function right before the instruction 
                builder.SetInsertPoint(I);
                builder.CreateCall(delayF);
                inserted = true;
            }

        }

}    
        return inserted;

}




/* Register the pass */
char DelayPass::ID = 0;
static llvm::RegisterPass<DelayPass> X("delaypass", "Insert calls to delay function.",
                                       false /* Only looks at CFG */, false /* Analysis Pass */);

// Automatically enable the pass.
static void registerDelayPass(const llvm::PassManagerBuilder &,
                              llvm::legacy::PassManagerBase &PM)
{
    PM.add(new DelayPass());
}
static llvm::RegisterStandardPasses
    RegisterMyPass(llvm::PassManagerBuilder::EP_EarlyAsPossible,
                   registerDelayPass);

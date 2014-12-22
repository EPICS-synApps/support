#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <asTrapWrite.h>
#include <dbAccess.h>
#include <epicsMessageQueue.h>
#include <epicsThread.h>
#include <epicsVersion.h>

#define GE_EPICSBASE(v,r,l) ((EPICS_VERSION >= (v)) && (EPICS_REVISION >= (r)) && (EPICS_MODIFICATION >= (l)))

static epicsMessageQueueId caputRecorderMsgQueue=0;
static int shutdown = FALSE;

static DBADDR dbaddr_cmd;
static DBADDR *paddr_cmd = &dbaddr_cmd;
static int valid_command_buffer=0;
static epicsThreadId threadId=0;
#define BUFFER_SIZE 100
#define COMMAND_SIZE 300
#define MAX_MESSAGES 20
typedef struct {
	int nchar;
	char command[COMMAND_SIZE];
} MSG;
#define MSG_SIZE sizeof(MSG)

#if GE_EPICSBASE(3,15,0)
/* we need dbNameOfPV() */

static char * dbCopyInNameComponentOfPV (
    char * pBuf, unsigned bufLen, const char * pComponent )
{
    unsigned compLen = strlen ( pComponent );
    if ( compLen < bufLen ) {
        strcpy ( pBuf, pComponent );
        return pBuf + compLen;
    }
    else {
        unsigned reducedSize = bufLen - 1u;
        strncpy ( pBuf, pComponent, reducedSize );
        pBuf[reducedSize] = '\0';
        return pBuf + reducedSize;
    }
}

unsigned dbNameOfPV (
    const dbAddr * paddr, char * pBuf, unsigned bufLen )
{
    dbFldDes * pfldDes = paddr->pfldDes;
    char * pBufTmp = pBuf;
    if ( bufLen == 0u ) {
        return 0u;
    }
    pBufTmp = dbCopyInNameComponentOfPV ( 
        pBufTmp, bufLen, paddr->precord->name );
    pBufTmp = dbCopyInNameComponentOfPV ( 
        pBufTmp, bufLen - ( pBufTmp - pBuf ), "." );
    pBufTmp = dbCopyInNameComponentOfPV ( 
        pBufTmp, bufLen - ( pBufTmp - pBuf ), pfldDes->name );
    return pBufTmp - pBuf;
}
#endif

int debug=0;
void myAsListener(asTrapWriteMessage *pmessage,int after) {
	DBADDR *paddr = pmessage->serverSpecific;
	char pvname[BUFFER_SIZE], value[BUFFER_SIZE], save[BUFFER_SIZE];
	MSG *msg;
	unsigned int numChar;
	long n=1, one=1, options=0;
	dbfType field_type;
	int i, j;

	if (after==0) return;
	if (debug) printf("myListener: %s@%s\n", pmessage->userid, pmessage->hostid);
	n = paddr->no_elements;
	field_type = paddr->field_type;
	numChar = dbNameOfPV(paddr, pvname, BUFFER_SIZE);
	if (debug) printf("myListener: field_type=%d, no_elements='%ld'\n", field_type, n);

	if (debug) printf("n==%ld, field_size==%d\n", n, paddr->field_size);
	if ((n>1) && (paddr->field_size==1)) {
		/* long string */
		dbGet(paddr, field_type, value, &options, &n, NULL);
	} else if (n>1) {
		/* we don't do arrays, unless they're actually long strings */
		dbGetField(paddr, DBF_STRING, value, &options, &one, NULL);
		strcpy(save, value);
		sprintf(value, "array(%s,...)", save);
	} else {
		dbGetField(paddr, DBF_STRING, value, &options, &n, NULL);
	}
	value[BUFFER_SIZE-1] = '\0';
	if (debug) printf("myListener: pvname='%s' => '%s'\n", pvname, value);
	
	msg = malloc(MSG_SIZE);
	/* if " in value, replace with \" */
	strcpy(save, value);
	for (i=0, j=0; i<BUFFER_SIZE; ) {
		if (save[j] == '"') value[i++] = '\\';
		value[i++] = save[j++];
	}
	n = snprintf(msg->command, COMMAND_SIZE-1, "%s,%s", pvname, value);
	msg->command[n] = '\0';
	msg->nchar = n+1;
	if (debug) printf("myListener: msg->command='%s'\n\n", msg->command);

	/* if (valid_command_buffer) dbPutField(paddr_cmd, DBF_CHAR, msg->command, n+1); */
    if (epicsMessageQueueTrySend(caputRecorderMsgQueue, &msg, MSG_SIZE)) {
        printf("myAsListener: message queue overflow\n");
    }
}

static void caputRecorderTask() {
    int msg_size;
	MSG *msg;
	while (!shutdown) {
		msg = NULL;
        msg_size = epicsMessageQueueReceiveWithTimeout(caputRecorderMsgQueue, &msg, MSG_SIZE, 5.0);
		if (msg_size != -1 && msg && valid_command_buffer) {
			dbPutField(paddr_cmd, DBF_CHAR, msg->command, msg->nchar);
			free(msg);
		}
	}
}

void registerCaputRecorderTrapListener(char *PVname) {
	asTrapWriteId id;
	long status;

	if (debug) printf("registerCaputRecorderTrapListener: entry\n");
	if ((status = dbNameToAddr(PVname, paddr_cmd)) != 0) {
		printf("registerCaputRecorderTrapListener: dbNameToAddr can't find PV '%s'\n", PVname);
		valid_command_buffer = 0;
		return;
	}
	valid_command_buffer = 1;
	id = asTrapWriteRegisterListener(myAsListener);
    if (!caputRecorderMsgQueue) {
        caputRecorderMsgQueue = epicsMessageQueueCreate(MAX_MESSAGES, MSG_SIZE);
    }

	if (!threadId) {
	    threadId = epicsThreadCreate("caputRecorder", epicsThreadPriorityLow,
	        epicsThreadGetStackSize(epicsThreadStackSmall),
	        caputRecorderTask, NULL);
	}
}

/*-------------------------------------------------------------------------------*/
/*** ioc-shell command registration ***/
#include <epicsExport.h>
#include <iocsh.h>

#define IOCSH_ARG		static const iocshArg
#define IOCSH_ARG_ARRAY	static const iocshArg * const
#define IOCSH_FUNCDEF	static const iocshFuncDef

/* int registerCaputRecorderTrapListener(char *filename); */
IOCSH_ARG       registerCaputRecorderTrapListener_Arg0    = {"PVname",iocshArgString};
IOCSH_ARG_ARRAY registerCaputRecorderTrapListener_Args[1] = {&registerCaputRecorderTrapListener_Arg0};
IOCSH_FUNCDEF   registerCaputRecorderTrapListener_FuncDef = {"registerCaputRecorderTrapListener",1,registerCaputRecorderTrapListener_Args};
static void     registerCaputRecorderTrapListener_CallFunc(const iocshArgBuf *args) {registerCaputRecorderTrapListener(args[0].sval);}

void caputRecorderRegister(void)
{
    iocshRegister(&registerCaputRecorderTrapListener_FuncDef, registerCaputRecorderTrapListener_CallFunc);
}

epicsExportRegistrar(caputRecorderRegister);


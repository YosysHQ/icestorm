// Written by Mathias Lasser
// License terms are unclear at the moment

#include<stdio.h>
#include<stdbool.h>
#include<stdlib.h>
#include<stdint.h>
#include<string.h>

int enable_debug=0;
#define debugf(...) do{if(enable_debug)fprintf(stderr,__VA_ARGS__);}while(0)

#pragma pack(2)

typedef struct 
{
    uint16_t    bfType;
    uint32_t   bfSize;
    uint16_t    bfReserved1;
    uint16_t    bfReserved2;
    uint32_t   bfOffBits;
}BITMAPFILEHEADER;

typedef struct 
{
    uint32_t    biSize;
    uint32_t    biWidth;
    uint32_t    biHeight;
    uint16_t    biPlanes;
    uint16_t    biBitCount;
    uint32_t    biCompression;
    uint32_t    biSizeImage;
    uint32_t    biXPelsPerMeter;
    uint32_t    biYPelsPerMeter;
    uint32_t    biClrUsed;
    uint32_t    biClrImportant;
}BITMAPINFOHEADER;

typedef struct{
 uint16_t boot_mode;
 uint16_t crc;
 uint8_t freq;
 uint8_t bank;
 uint32_t write_pointer;
 
 uint32_t CRAM_rowsize;
 uint32_t CRAM_colsize;
 uint8_t* CRAM[4];
 uint32_t BRAM_rowsize;
 uint32_t BRAM_colsize;
 uint8_t* BRAM[4];
}FPGA_t;

typedef struct{
 uint32_t len;
 uint32_t pointer;
 uint16_t crc;
 uint8_t payload[0];
}bitstream_t;

typedef union{
 struct{
  uint8_t lo:4;
  uint8_t hi:4;
 };
 uint8_t full;
}nibble_t;

const char* freq_settings[]={"low","medium","high"};
const char* boot_settings[]={"Disable","Enable"};

uint16_t crc16(uint32_t crc,uint8_t in){
 for(int i=7;i>=0;i--){
  crc<<=1;
  if((crc^(in<<(16-i)))&0x10000)
   crc^=0x1021;
 }
 return crc;
}

uint32_t get_byte(bitstream_t* bitstream){
 if(bitstream->pointer>=bitstream->len)return 0xFFFFFF;
 uint8_t data=bitstream->payload[bitstream->pointer++];
 bitstream->crc=crc16(bitstream->crc,data);
 return data;
}

uint32_t get_payload(bitstream_t* bitstream,int len){
 uint32_t ret=get_byte(bitstream);
 for(int i=1;i<len&&ret!=0xFFFFFFFF;i++){
  ret<<=8;
  ret|=get_byte(bitstream);
 }
 return ret;
}

void FPGA_write(FPGA_t* FPGA,bitstream_t* bitstream){
 int n=FPGA->CRAM_colsize*FPGA->CRAM_rowsize/8;
 uint8_t* temp=(uint8_t*)malloc(n);
 for(int i=0;i<n;i++)
  temp[i]=get_byte(bitstream);
 FPGA->CRAM[FPGA->bank]=temp;
}

void FPGA_EBR_write(FPGA_t* FPGA,bitstream_t* bitstream){
 int n=FPGA->BRAM_colsize*FPGA->BRAM_rowsize/8;
 uint8_t* temp=(uint8_t*)malloc(FPGA->write_pointer+n);
 if(FPGA->write_pointer!=0){
  uint8_t* old_data=FPGA->BRAM[FPGA->bank];
  memcpy(temp,old_data,FPGA->write_pointer);
  free(old_data);
 }
 for(int i=0;i<n;i++)temp[FPGA->write_pointer++]=get_byte(bitstream);
 FPGA->BRAM[FPGA->bank]=temp;
}

int parse(bitstream_t* bitstream, FPGA_t* FPGA) {
 uint32_t preamble=0;
 while(1){
  preamble<<=8;
  preamble|=get_byte(bitstream);
  if(preamble==0x7EAA997E){
   debugf("Got preamble\n");
   break;
  }
  if(preamble==0xFFFFFFFF){
   fprintf(stderr,"Error: could not find preamble...\n");
   return -1;
  }
 }
 nibble_t command;
 uint32_t payload;
 uint16_t crc;
 while(1){
  crc=bitstream->crc;
  command.full=get_byte(bitstream);
  if(command.full==0xFF){
   payload=get_byte(bitstream);
   if(payload!=0x00)goto err;
   char*comment=(char*)&bitstream->payload[bitstream->pointer];
   debugf("Got comment section start\n");
   while(1){
    payload<<=8;
    payload|=get_byte(bitstream);
    if((payload&0xFFFF)==0x00FF)break;
    if(payload==0xFFFFFFFF){
     fprintf(stderr,"Error: could not find comment section end\n");
     return -1;
    }
   }
   debugf("\n%s\n\n",comment);
   debugf("Got comment section end\n");
   continue;
  }
  payload=get_payload(bitstream,command.lo);
  switch(command.hi){
  case 0x0:
   if(command.lo!=0x01)goto err;
   switch(payload){
   case 0x01:
    debugf("Write to CRAM!!!\n");
    FPGA_write(FPGA,bitstream);
    get_payload(bitstream,2);
    break;
   case 0x03:
    debugf("Write to BRAM!!!\n");
    FPGA_EBR_write(FPGA,bitstream);
    get_payload(bitstream,2);
    break;
   case 0x05:
    debugf("Resetting CRC\n");
    bitstream->crc=0;
    break;
   case 0x06:
    debugf("Wake up\n");
    return 0;
   default:
    goto err;
   }
   break;
  case 0x1:
   if(command.lo!=0x01)goto err;
   if(payload>3){
    fprintf(stderr,"Error: bank %u does not exist...\n",payload);
   }
   debugf("Set bank to %u\n",payload);
   FPGA->bank=payload;
   break;
  case 0x2:
   if(command.lo!=0x02)goto err;
   debugf("CRC check: %04X %04X\n",payload,crc);
   break;
  case 0x5:
   if(command.lo!=0x01)goto err;
   if(payload>2){
    fprintf(stderr,"Error: unknown frequency setting...\n");
    return -1;
   }
   debugf("Boot frequency set to %s\n",freq_settings[payload]);
   FPGA->freq=payload;
   break;
  case 0x6:
   if(command.lo!=0x02)goto err;
   payload++;
   debugf("Row size:    %i\n",payload);
   if(FPGA->CRAM_rowsize)FPGA->BRAM_rowsize=payload;
   else FPGA->CRAM_rowsize=payload;
   break;
  case 0x7:
   if(command.lo!=0x02)goto err;
   debugf("Column size: %i\n",payload);
   if(FPGA->CRAM_colsize)FPGA->BRAM_colsize=payload;
   else FPGA->CRAM_colsize=payload;
   break;
  case 0x8:
   if(command.lo!=0x02)goto err;
   if(payload==0x0000){
    debugf("Reset write pointer\n");
    FPGA->write_pointer=0;
   }
   else if(payload==0x0080){
    debugf("Don't reset write pointer\n");
   }
   else goto err;
   break;
  case 0x9:
   if(command.lo!=0x02)goto err;
   if(payload&0xFFDF){
    fprintf(stderr,"Error: Unknown warmboot setting... %04X\n",payload);
    return -1;
   }
   debugf("%s warmboot\n",boot_settings[payload?1:0]);
   FPGA->boot_mode=payload;
   break;
  default:
   goto err;
  }
 }
err:
 fprintf(stderr,"Error: unkown command... %08X\n",bitstream->pointer);
 return -1;
}

uint8_t get_CRAM_bit_from_sector(FPGA_t* FPGA,int bank,int x,int y){
 if(x<0||x>=FPGA->CRAM_rowsize)return 0xFF;
 if(y<0||y>=FPGA->CRAM_colsize)return 0xFF;
 if(bank<0||bank>=4)return 0xFF;


 int bit=y*FPGA->CRAM_rowsize+x;
 int pointer=bit>>3;
 int shifts=7-(bit&7);
 return (FPGA->CRAM[bank][pointer]>>shifts)&1;
}

int tiles[2][20]={
 {18,54,54,42,54,54,54},
 {18,2,54,54,54,54,54,54,54,42,54,54,54,54,54,54,54,54}
};

int permx[2][18]={
 {23,25,26,27,16,17,18,19,20,14,32,33,34,35,36,37,4,5},
 {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17}};
int permy[4][16]={
 {0,1,3,2,4,5,7,6,8,9,11,10,12,13,15,14},
 {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15},
};

int tile_row_size[2]={7,17};
int tile_col_size[2]={9,17};

void print_tile(FPGA_t* FPGA,int x,int y){
 int type=FPGA->CRAM_rowsize==872;
 int dirx=0;
 int diry=0;
 int tx=x;
 int ty=y;

 int corner_flags=0;
 if(x==0)corner_flags|=1;
 if(y==0)corner_flags|=2;
 if(x==tile_row_size[type]*2-1)corner_flags|=4;
 if(y==tile_col_size[type]*2-1)corner_flags|=8;
 if(corner_flags&(corner_flags-1))
  return;

 if(x>=tile_row_size[type]){
  dirx=1;
  tx=tile_row_size[type]*2-1-x;
 }
 if(y>=tile_col_size[type]){
  diry=1;
  ty=tile_col_size[type]*2-1-y;
 }
 int sector=(diry|dirx<<1);
 int offx=0;for(int i=0;i<tx;i++)offx+=tiles[type][i];
 if(corner_flags){
  printf(".io_tile %i %i\n",x,y);
  for(int cy=0;cy<16;cy++){
   for(int cx=0;cx<18;cx++){
    int val;
    if(corner_flags&5){
     if(diry){
      val=get_CRAM_bit_from_sector(FPGA,sector,offx+tiles[type][tx]-1-permx[1][cx],ty*16+15-permy[1][cy]);
     }else{
      val=get_CRAM_bit_from_sector(FPGA,sector,offx+tiles[type][tx]-1-permx[1][cx],ty*16+permy[1][cy]);
     }
    }else{
     if(dirx){
      val=get_CRAM_bit_from_sector(FPGA,sector,offx+tiles[type][tx]-1-permx[0][cx],ty*16+15-permy[0][cy]);
     }else{
      val=get_CRAM_bit_from_sector(FPGA,sector,offx+permx[0][cx],ty*16+15-permy[0][cy]);
     }
    }
    printf("%i",val);
   }
   printf("\n");
  }
 }
 else{
  if(tiles[type][tx]==20)printf(".io_tile %i %i\n",x,y);
  if(tiles[type][tx]==42)printf(".ram_tile %i %i\n",x,y);
  if(tiles[type][tx]==54)printf(".logic_tile %i %i\n",x,y);
  for(int cy=0;cy<16;cy++){
   for(int cx=0;cx<tiles[type][tx];cx++){
    printf("%i",get_CRAM_bit_from_sector(FPGA,sector,(dirx?(offx+tiles[type][tx]-1-cx):(offx+cx)),(diry?(ty*16+(15-cy)):(ty*16+cy))));
   }
   printf("\n");
  }
 }
}

int main(int argc,char**argv) {
 if(argc>=2&&!strcmp(argv[1], "-v")) {
  enable_debug=1;
  argc--;
  argv++;
 }
 if(argc!=2) {
  fprintf(stderr,"iceunpack [-v] input\n");
  return 1;
 }

 FILE*r_file=fopen(argv[1],"rb");
 if(r_file==NULL) {
  fprintf(stderr,"could not open %s\n",argv[1]);
  return 1;
 }
 fseek(r_file,0,SEEK_END);
 size_t r_size=ftell(r_file);
 fseek(r_file,0,SEEK_SET);

 bitstream_t* bitstream=(bitstream_t*)malloc(sizeof(bitstream_t)+r_size);
 bitstream->len=r_size;
 bitstream->pointer=0;
 fread(bitstream->payload,1,r_size,r_file);
 fclose(r_file);

 FPGA_t FPGA;
 memset(&FPGA,0,sizeof(FPGA));

 parse(bitstream,&FPGA);
 free(bitstream);

 printf(".device 1k\n");
 for(int y=0;y<18;y++)for(int x=0;x<14;x++)print_tile(&FPGA,x,y);
 return 0;
}

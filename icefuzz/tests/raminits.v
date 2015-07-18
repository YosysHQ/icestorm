// tmpfiles/ex_00.v
module top (
  input clk,
  input [7:0] sel,
  input [15:0] wdata,
  output [15:0] rdata,
  input [7:0] addr
);
  wire [15:0] rdata_0301;
  SB_RAM256x16 ram_0301 (
    .RDATA(rdata_0301),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 0),
    .MASK(16'b0)
  );
defparam ram_0301.INIT_0 = 256'heee7d4195b1ee583e83766c47c4279255c36fac37ffa2db1c7978834c0a7b756;
defparam ram_0301.INIT_1 = 256'haf36df1852690a6f4bd5a70c8cdc7ace32570591bdc9da916fdfebbf250ee920;
defparam ram_0301.INIT_2 = 256'h062ec86b566ae81511bdb1c797b09358fd7b8b55a4033809181a8590636ebc4a;
defparam ram_0301.INIT_3 = 256'he5647bccd28fcd7e1175dd08c07eee22b5f7a76ce80b814acc913a8bf6272489;
defparam ram_0301.INIT_4 = 256'h847367636b8515d939efbb8e215509b3639c2d42650023fde29a300331ea02dd;
defparam ram_0301.INIT_5 = 256'h1bfed331fc20e7d3855f6f57b704e77098ad9921daa03a251a0d4750cfdb8c5c;
defparam ram_0301.INIT_6 = 256'h5796d45e174c10a14c1c6296d8e71d33a2601b790ac8ace68483a4095b8b2f2c;
defparam ram_0301.INIT_7 = 256'h5c02f2a5a09d26529a93bdc1c3b2dad1edbdba8729e3ba1447b96a823b5e6ddb;
defparam ram_0301.INIT_8 = 256'he6c0da7b269cb3b8213608a7c38a5eb224f7d37981f337e1b1f4e4aa13a330bc;
defparam ram_0301.INIT_9 = 256'hd8aab74a136340b43c44e69b99233b7657c1faf8795e6e6513e399eccf835d64;
defparam ram_0301.INIT_A = 256'h76da9bfa7def43d27b289046765ebad19bd9853133aa79e7a4c53b489266b78b;
defparam ram_0301.INIT_B = 256'hd0be66fe7f334ca37b5cfa6fcfb84f2b5d7b556e3b179da25cb20a4bcf285dbc;
defparam ram_0301.INIT_C = 256'he36823bd57f798408173ee4e1a138496a319039e28f783015ad938818b1ffeef;
defparam ram_0301.INIT_D = 256'h19ad3217524d84a9eed19f6a88a3e6f6f3e27c256534dcefe6721a2eaf27e104;
defparam ram_0301.INIT_E = 256'hbb5e5ef9246e61ee24121f2169dc1d755429486f030b7ae134f83c35915a2f44;
defparam ram_0301.INIT_F = 256'hf0b5e781fb75db80882e0641026b6c4df0e61dd31d84c2f44bbe7073ccad1d01;
  wire [15:0] rdata_0303;
  SB_RAM256x16 ram_0303 (
    .RDATA(rdata_0303),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 1),
    .MASK(16'b0)
  );
defparam ram_0303.INIT_0 = 256'h2b668f5787aef8f5025f79512dcefc91d4bebc46513598e42c93d37c931d8923;
defparam ram_0303.INIT_1 = 256'h7b9a84f2d5f65df84d4157495ab21e01e152dd7a886c33cb614e382e7fed9eab;
defparam ram_0303.INIT_2 = 256'h878bdd512303597de1345a1cc680af906dabb3a7ad0ff50221288bce8af64881;
defparam ram_0303.INIT_3 = 256'he36b5511c45aec1bba20d1791c3ccfa39cf93bde842f184cc1a93d70520529d6;
defparam ram_0303.INIT_4 = 256'haf4b39a9fdfb42ccae9f2eea59845f5a8c2fb07035d64d71722f4d656b703c69;
defparam ram_0303.INIT_5 = 256'h4c0cacce82085c0931587d9e7f4e6d074746cca6744b4a3b0ab1b54ec03fc84e;
defparam ram_0303.INIT_6 = 256'he937cdb315288fbfdcaf1d77b698da022e5f6cf1b4fa3249d0d50eaf876466ae;
defparam ram_0303.INIT_7 = 256'h1bd6d490c00964563d3f8438a32966a8f5de9447eae7b0e63dbf930d2dad4faa;
defparam ram_0303.INIT_8 = 256'h55f0e909449d025ca05f81ffe6a71641b98694281522061a7d60fc84447395af;
defparam ram_0303.INIT_9 = 256'h03cbdbbb3afb93d1360dc27ee9bc65b9dd407010717a2e5d5a2e6d7195875aef;
defparam ram_0303.INIT_A = 256'hc8f9ceb334e4c22b1bfbd0321ab6762af2d10f9e67282aa4b3c0b4784c061708;
defparam ram_0303.INIT_B = 256'h4a49021a4cf723dca9d9dba93f8ae9f3d5be64f54d61b5b40646bc8f11418390;
defparam ram_0303.INIT_C = 256'hd579caee533c14990f0ef6e2307cbfd1252414b9384802fa7b434e40cc8b1f21;
defparam ram_0303.INIT_D = 256'h17ff7be7f32b4e90a04b999795a68ecf923fd605ae58d82f9ddf78adfff85572;
defparam ram_0303.INIT_E = 256'h41f8121524de634c0801dc5f8c04c8dec086b1f63d3e3a769c9cd63fd8132a72;
defparam ram_0303.INIT_F = 256'h32d4549b468eba9a49fb496ff2d11b8e43d138b24a800e49853a6aba5bb5c5a2;
  wire [15:0] rdata_0305;
  SB_RAM256x16 ram_0305 (
    .RDATA(rdata_0305),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 2),
    .MASK(16'b0)
  );
defparam ram_0305.INIT_0 = 256'h172521cfcd66a4e54fdd281bea4e877d13357371970a607c4f1ec21bb92550c1;
defparam ram_0305.INIT_1 = 256'h570a6f1ceb613a885a738b85084a55cf2e1d619a5392390c972d53e0b3c11f5d;
defparam ram_0305.INIT_2 = 256'hb630e33faca35036486f0b8f94f0a4b21f804a2d82799ab121141b3ab1ba8df4;
defparam ram_0305.INIT_3 = 256'haf7d9e3eb70911e8af4f2a1aad6cbfaa69248b89b36c222f7b1a5c32aa3844a4;
defparam ram_0305.INIT_4 = 256'h273c5c3dcea0d9942168d6181aaaa30efbc3efd5fff73c7f30de4bdacd018779;
defparam ram_0305.INIT_5 = 256'h559c7a4af1d4c9204d935d10817727b1ca5c554580e8b28dfc9e2fd6f2c71e77;
defparam ram_0305.INIT_6 = 256'h418602bdff1e69af57af6a198e57a59c68443f3934fdd09ee68e630304166940;
defparam ram_0305.INIT_7 = 256'h54aac47c7be964002b6c71aec829d69dc6ef2ee6f3640279b8c7f7947b4a2e61;
defparam ram_0305.INIT_8 = 256'h32b50c21a7bdbdfac5909853b9d0fa8915dadc18f087070e30fba834d6eab209;
defparam ram_0305.INIT_9 = 256'h02742ea4a2b626738ce04c7f6b4472739f981a7dd37413214228c9446ab320cb;
defparam ram_0305.INIT_A = 256'h5c70fe89a21724eb2d36ded6fd01f47da78a97db0666e038cc5284ffaf5e66e1;
defparam ram_0305.INIT_B = 256'h7ffdc072c4f7abc5888f3d30aa097195aa54f18635ad8308e08d3cda939db459;
defparam ram_0305.INIT_C = 256'h159a2eaace991c51eb3c61abe9fe74af235d51f04ebabf0b2c0f0dfe6e3bb4e6;
defparam ram_0305.INIT_D = 256'h460ded1b0a7f120b23cd292508e5a575fa8fd66f3033b69ab189e110fae0d668;
defparam ram_0305.INIT_E = 256'hc72b4562d113f6f9c58ba44a7edf53b39b664357e12296fc389bd05d098311ee;
defparam ram_0305.INIT_F = 256'h69bb7c5e08c96718f7ad092ba30a40c3b4347572251976ab0d1cae6bbac50333;
  wire [15:0] rdata_0307;
  SB_RAM256x16 ram_0307 (
    .RDATA(rdata_0307),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 3),
    .MASK(16'b0)
  );
defparam ram_0307.INIT_0 = 256'hf59c43dc52bc3d2b7bd85cd8c56aabb48969aae3721d16db0ff0524dabde709b;
defparam ram_0307.INIT_1 = 256'heff0fb7181e53b6512b080104e27b8e18c62780045a8106caf69951ca6173db4;
defparam ram_0307.INIT_2 = 256'hbfcb9c012c6c74f22b40ebe0369f994c9e409a65cd018bacb6dc6c3da36a6652;
defparam ram_0307.INIT_3 = 256'h7ea21da12871042efd405fe9998f635050a02f99e9b802cfec48d38fe984f30a;
defparam ram_0307.INIT_4 = 256'h5b659e0511fe236eb30e9fe92c5d69a637a10ab807a98eb567c2e914431a96fe;
defparam ram_0307.INIT_5 = 256'h6a7816f542396924307d31d55501a35849b2531f4ca596a29e84cb3c650b4062;
defparam ram_0307.INIT_6 = 256'he278bbc6ce05e58f6d15b005337aa2abdc6866ce8fc74cda53e9393909662f49;
defparam ram_0307.INIT_7 = 256'h353257b35760e5d107ec73be367dbcef8e9d6f4c227f436758f569bc325ac59f;
defparam ram_0307.INIT_8 = 256'h83609202f72286d35700331a86c68f0b1f20d8c0dd39bf0e7652cda584bec453;
defparam ram_0307.INIT_9 = 256'hf24f9f1dca3539dcc73bd15a1c3b12e4f27d864325c1eb2f5f7c5e9ab0c6ec68;
defparam ram_0307.INIT_A = 256'h2f41690287a95877a8637624974e1d779aa82daa7f1439733a7bcd7ee6a7d6df;
defparam ram_0307.INIT_B = 256'h4d3e73056bebe5184c7fbacd65b2862c66c425d3b82ac573ab4b325035a9cff1;
defparam ram_0307.INIT_C = 256'hf2dd4cf5279f86c413dc082dfc3b8e1dd913b59118dac6c99cde6e4a487316a2;
defparam ram_0307.INIT_D = 256'haa901c2b6d47194f2157465b276bc2cb30c8af04f6372384f969e26235a1fc6b;
defparam ram_0307.INIT_E = 256'h7cacd0b5a31ca17fdf94837ffa560342e9aa8ec69626dfd0b33b4df263d1fb88;
defparam ram_0307.INIT_F = 256'h0da63678ff1980428f183ce9f9317dd0f2e0ad40f9c55b89342db6e18b832977;
  wire [15:0] rdata_0309;
  SB_RAM256x16 ram_0309 (
    .RDATA(rdata_0309),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 4),
    .MASK(16'b0)
  );
defparam ram_0309.INIT_0 = 256'h07a51489176ecf26b26ba3d3f4acb14b927e4f80c1a3333e79f52b87d0052eba;
defparam ram_0309.INIT_1 = 256'he542c4ed986aef41e2c1f1f1e0eff957f5f7fe3c1a956f1b7e73f6c12c3e7b35;
defparam ram_0309.INIT_2 = 256'h08e0d0315d86c998bfce1650d75c4cba11db471ff568d0ad39078ee3ad2dd5ae;
defparam ram_0309.INIT_3 = 256'h0624c556f3b27168ca874071a2c037eba979cb6738a8983c26017669cd44f3f9;
defparam ram_0309.INIT_4 = 256'h8f3727f57d00cdfdb0766c85a68bb59c52691d4b154bc2017cb2f0cf9deac2de;
defparam ram_0309.INIT_5 = 256'he2d9ad2f0193ddb2ca738bed9d69fff0c4e181c5f6534a986fcb65d1756b0f5d;
defparam ram_0309.INIT_6 = 256'hd28fc8443c5006206c35efd0fb2e0504f8d08f788e276b9f642d6837897906bc;
defparam ram_0309.INIT_7 = 256'h9d25639c0a8e04cdb1fd5e02583734811a349e6ebfb3913e775e5fc09dbd8536;
defparam ram_0309.INIT_8 = 256'h845c59e1f7c470abce8fa54120e38a9ff002c46c0eb2b651d3120627df47fa65;
defparam ram_0309.INIT_9 = 256'h709ef0f92579008ec26a7bb4aa70870557693cc59c4e16347e23574429b1acaa;
defparam ram_0309.INIT_A = 256'hd3553eac767b972d7cbec91901fdf203768c337577e599929a02788bab131ba2;
defparam ram_0309.INIT_B = 256'hbcb398877ab4e802f93de666ee53147b4104a883e8fc58f704764bb0377457aa;
defparam ram_0309.INIT_C = 256'hcb6bcd60cbeec7d69627cb56da8e829171c72a8f9ae075ca73146cb3bb33895f;
defparam ram_0309.INIT_D = 256'hec0a7b61ca77b184a5da828074adee07b0bdaf9d3a75f0b4e496228906882c96;
defparam ram_0309.INIT_E = 256'h4fcaff83f49c993e1344167d32660a6693a730fa2f29d5d4cab9063853bd7bbe;
defparam ram_0309.INIT_F = 256'h0238e69d220727869654edd6fa05d2e9f17b82827fdf7e151d0078147fe5bdff;
  wire [15:0] rdata_0311;
  SB_RAM256x16 ram_0311 (
    .RDATA(rdata_0311),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 5),
    .MASK(16'b0)
  );
defparam ram_0311.INIT_0 = 256'h1e29fa340abb28a034d044905ef2b7aa08b76a1dafc7e743bdfc4fe88d77bb02;
defparam ram_0311.INIT_1 = 256'h2fed2793ab9de32ba8d11df985a68371bdfb9564ccb8c12c63aa9c968b95b348;
defparam ram_0311.INIT_2 = 256'hc3603ba144d8f2e8273b7762172a862f179e043fc755912fe840c60eb0aafc5f;
defparam ram_0311.INIT_3 = 256'hbe3c00c259e270eec9ab5ca99a40653662bdc9ba0b0742eddc9da27441c29907;
defparam ram_0311.INIT_4 = 256'h2effdb8a2a1ad09741d463bafe42d24e684e5c271cb64911f33651abb2554217;
defparam ram_0311.INIT_5 = 256'h3d12ab8b32a2f8e90e616ba6136747522f6ef4b3ef3231750a6a6da587c46544;
defparam ram_0311.INIT_6 = 256'hb9b1d4f05a71ca7bc92e7ef599655af7ca4abdc9a6bdb0ca6c9a1b2de1b67e6f;
defparam ram_0311.INIT_7 = 256'ha2601f9d00bcab3ca1ec26151124156e6cf0f2c45f4761bdfb4f3ea6d0b9789c;
defparam ram_0311.INIT_8 = 256'h16012927b00b193efde7ca215c88573280cea742d31623de3e0ed88b5a08e23c;
defparam ram_0311.INIT_9 = 256'h5b1657e14902f7c08b6c154f96e04192d52439983d0a5c8810d0462f45d1c091;
defparam ram_0311.INIT_A = 256'hdc67eaa704ff2aa09386be4dc9448074c427139cbb5118273a954a53838ffecf;
defparam ram_0311.INIT_B = 256'h347c2253402c45890e871a1dbe53cd91e98b3cb4c1884c349e9536fcc1e5b53f;
defparam ram_0311.INIT_C = 256'hc22e14b25ffdfb89a0556700e8171d0dfc84eb865898e6280cdbf0dbf51ec78c;
defparam ram_0311.INIT_D = 256'h9fc88e0a32800fcb117c996b5dc252ec0256ccf1cecfccb0f2bfd5870219878c;
defparam ram_0311.INIT_E = 256'h69df52b9aa92b8f75eb961cb77e1753ce5da5400f412bd36bc5c274a58fe17c2;
defparam ram_0311.INIT_F = 256'h96dda78bb769a16e24ad1d9c34604b35c450c79d6fd2e51b28320a1bdd2408b0;
  wire [15:0] rdata_0313;
  SB_RAM256x16 ram_0313 (
    .RDATA(rdata_0313),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 6),
    .MASK(16'b0)
  );
defparam ram_0313.INIT_0 = 256'hd9559cc61e3f4571d58b14ea4740e577d14c30ebdf4f73b8c782f46f3b6c08d1;
defparam ram_0313.INIT_1 = 256'h6f4efcd9b858d443ac63f0fd9225592fdba22f66c1eccb3714aa800ed71412ba;
defparam ram_0313.INIT_2 = 256'h0ab1107b6d650fdf66add2cc2a7e488108161e3e651486f00ad50b3c070e68c3;
defparam ram_0313.INIT_3 = 256'h37ffb1dc247db3f4b69ca946e62587246b0806f819735c9261c4cbfd46769b71;
defparam ram_0313.INIT_4 = 256'hb436465a2f3a75b373c8a2013106750d96cd433c935988591a46c2cf947a4fc0;
defparam ram_0313.INIT_5 = 256'h97752e46f2a5658b7a242904bbe1e26748ba95bf6f7e9a6ff72373e9a3f5dcc0;
defparam ram_0313.INIT_6 = 256'h2f25d930c7bea790540df0b90418e26c86c58cba0f3cfd2e20c1adfafc8b58b9;
defparam ram_0313.INIT_7 = 256'hf67a98264a755ad033da5a3f4f7bb0563a24c65f9e379e7ea24398ff770a1569;
defparam ram_0313.INIT_8 = 256'h1a9d43cfcd1ae2142b2f35e8eb1f961e20f3488685a817ea0f7147abefe92821;
defparam ram_0313.INIT_9 = 256'hb3c30dcac4dccdad0c7e14a9fa41edd57fb93a1560cfad9fffe812b476a66bcf;
defparam ram_0313.INIT_A = 256'hda6c916c9a250420b9470d5bb5f4895bc65f83f3418d7872734951b3c89f8157;
defparam ram_0313.INIT_B = 256'ha09ff972ebcbd082333bc97a4687b5b5f7b3a7939d7f4a6d3728cfa5a6599e93;
defparam ram_0313.INIT_C = 256'h38eb42c565b9f9ebe0596a1fa9f9fc33836fca4058e1e20f60069ecbde0a1a05;
defparam ram_0313.INIT_D = 256'h4beeab82252f2569fb56ffad4478db381e6b0d96b7f6d712c7073d8a118a5892;
defparam ram_0313.INIT_E = 256'h0b48f12af2ff6febee038a01ae79d93cac9f09ac76501e43bb4817d39f1d043d;
defparam ram_0313.INIT_F = 256'hdfbaa596a11d2248f849620d20cf3a6f856302c5bcc74dd6bfb3a756f59446c3;
  wire [15:0] rdata_0315;
  SB_RAM256x16 ram_0315 (
    .RDATA(rdata_0315),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 7),
    .MASK(16'b0)
  );
defparam ram_0315.INIT_0 = 256'h2af31f7e9493844389075cf4a347ad1ded317b44870c068432d89047eeca2b37;
defparam ram_0315.INIT_1 = 256'hf51a6444eba4fb0b4baef416aa19593cf6ab473fe46255e53550cc8523ccb1fc;
defparam ram_0315.INIT_2 = 256'h09f3a52d859af19ba525a62fccf0b64d03a86be72316ce8f38acb5959db215f5;
defparam ram_0315.INIT_3 = 256'hfe309f2ae03cb8f724c01818371d5456ff5c9ef029f4806597554044d23fca5c;
defparam ram_0315.INIT_4 = 256'h13bbbf3bb5e83b3200dde2fa4ef0566f4fcb2bee140ab81acf351cfad0a9d1cb;
defparam ram_0315.INIT_5 = 256'h73b9f5bff710c59328c47ff675d8b68cdd2cfc07aa71d66b29ff98500b70e063;
defparam ram_0315.INIT_6 = 256'h24d0607d548133d0f4e50d79b643fc604de016ca3d849c9e1fa5d70357f443c7;
defparam ram_0315.INIT_7 = 256'hab53d6af5f0b3c6d7710bb402e21438013f3ac830c6405e219b3f114ad5b4db2;
defparam ram_0315.INIT_8 = 256'h268b8fc89f948592c8e2fb38912dbd2bc88e67e820d03f5b4cf494491ac36816;
defparam ram_0315.INIT_9 = 256'h846a486f199955e0852705305a805d5cece1647e839d3cd811a7a9d197f84815;
defparam ram_0315.INIT_A = 256'h09007c4a495b836c16a082cd2418b2962059924230aa7729d1bb2be706283998;
defparam ram_0315.INIT_B = 256'h336ee10a1530f40a98d338e2dceb777d8f6b456431c2267dcfda449bf5d28ed4;
defparam ram_0315.INIT_C = 256'h1b16770684b88454ab9db7e40b07802b36d741eeacebc9d1648723b857f2ba4b;
defparam ram_0315.INIT_D = 256'h9ccb7b57c9d5f4ac9eb293df84b6a124d1dde80bc7f262e38af79177e6520243;
defparam ram_0315.INIT_E = 256'hab117e08b2b8ddcd7f68311478c2e018799685480835f1dc30b9159377ff2d69;
defparam ram_0315.INIT_F = 256'hb05b0092e8d80ea1ff04a52f94d9b7f147f5651e8b624c1d800ce228e9db35e4;
  wire [15:0] rdata_1001;
  SB_RAM256x16 ram_1001 (
    .RDATA(rdata_1001),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 8),
    .MASK(16'b0)
  );
defparam ram_1001.INIT_0 = 256'h9c7c41b50768a605cf8152a411317da39cf38541b53e6cab1f59fd2ff79f1b29;
defparam ram_1001.INIT_1 = 256'h2cb583fde53060648977748557fe9480afb7e331806f1955e4cb348795a15d4a;
defparam ram_1001.INIT_2 = 256'hfc57e12bed42aa24b833f3f2e8a254f8d17dbaefde4ef4fa78f14f96bb248b1d;
defparam ram_1001.INIT_3 = 256'h6fa44ad672bb75f06d5e00fe4d735e528400897f0eaec902ec089786e9e0968d;
defparam ram_1001.INIT_4 = 256'h1ce5e5112b8ab585513bcb8ef393e593ddd5d0e76af31aaa4e815e680eea7d1d;
defparam ram_1001.INIT_5 = 256'hc338e533ee20665b272c18f0b85424e41745d7649fad5736f68677b92feaba2c;
defparam ram_1001.INIT_6 = 256'hf1ba42579571926ee12e8abbd287acf12d22a10caecce7b310dd7e75dde1bb7d;
defparam ram_1001.INIT_7 = 256'hf4b97664ff2e90cb650c33d660c8e03898a7c0f608c58667867bb9f0c4042b77;
defparam ram_1001.INIT_8 = 256'h03c5c843009d4ce9457a900cc6c45ca871bcf29e8c206b85bc1f7637e5afddd2;
defparam ram_1001.INIT_9 = 256'hae78d5d9491ce25d1c833158e72dc0b440f91d1acce4bc33cddcf8a63885b8a6;
defparam ram_1001.INIT_A = 256'hff813a16814de988dd1d99c902ccba4c070623d63935bc59ca9a54f8811d97b8;
defparam ram_1001.INIT_B = 256'h0644e9960a194d65fed04e16f0f45d6ddf1aa911f13da01696dce1e5fdff6a9a;
defparam ram_1001.INIT_C = 256'h93aa1fbc2c2f92dbec99d4e59741569b7a5fef853715af2e069b19fb50a1b934;
defparam ram_1001.INIT_D = 256'hbdfc5a6a699eb6c6a6857c6b2ff4ef867084d4db40cdc5babd878ec8a5b9f0ea;
defparam ram_1001.INIT_E = 256'h0d3751acaa17328f1e52fd4443755392bc4d20b626185b200c87677191df6259;
defparam ram_1001.INIT_F = 256'h7772f629fcb9aff2a3318a98b9e4e58f44fd902bf544239968d748796577ca6a;
  wire [15:0] rdata_1003;
  SB_RAM256x16 ram_1003 (
    .RDATA(rdata_1003),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 9),
    .MASK(16'b0)
  );
defparam ram_1003.INIT_0 = 256'h52f7a59fb8d848aad51bd38121e11d5175b3239b971a8bcbd270d276e4f21f90;
defparam ram_1003.INIT_1 = 256'h19a6611c09a950d1045425ecee7977d0f3bd3b70cce0ade0aa10f5fe3f15b1d3;
defparam ram_1003.INIT_2 = 256'hff16259d190b5d0dd4453df81d9375dc1768e22673be4905fcc51f0f975e2cd1;
defparam ram_1003.INIT_3 = 256'ha32a34f06674fd42bc1c9533c378d01b65cbce95a7200b64f9dde478cbb754b7;
defparam ram_1003.INIT_4 = 256'hf6d4f68fd768de9aa637f5755cc3f64248d0f9866c5fcb00bd79be9d247243f8;
defparam ram_1003.INIT_5 = 256'hb2411f4b8b21802fbce0082920a96856c9902897538f7068c10ebe6dca1ff7d6;
defparam ram_1003.INIT_6 = 256'h2b3b94e10d954bc10b97e227f5b2c1c629e62166ed06c2347bfb2fa4a44010ea;
defparam ram_1003.INIT_7 = 256'hff82fa877fbf9802434a2f8f8eff7a18e6b9ad444f736c1592db47627146289e;
defparam ram_1003.INIT_8 = 256'hfced2cd513690efbd52ded9fe01bb809a8d2b048326d0e7559d8c181cf6d075f;
defparam ram_1003.INIT_9 = 256'hba7672c199d70b9d2b3d5c980aad280086feeacbe16077b94941ac9ebe9c7aa4;
defparam ram_1003.INIT_A = 256'heb9d91de7a2ffabce82eead39a8ee44eb1b65a7274ead34013422c9f7cb0bcd7;
defparam ram_1003.INIT_B = 256'h2fbc5beec9c515ca4d0186e649eb7475e5170e7ea4b6e0e3de09f96b98a4216c;
defparam ram_1003.INIT_C = 256'hd146f604f32aea162557efc77e070a9edbbad0d276024acf16d1a5dd4629d48d;
defparam ram_1003.INIT_D = 256'h445080680263cbe9b1dec849f5dba0449c1a105981a3ad167e346303742edf2f;
defparam ram_1003.INIT_E = 256'h0527a9fbf0a68e910b8589e3bb1efa281615e6857d5cdb78ece71aeb9f69de3d;
defparam ram_1003.INIT_F = 256'h9282f9309931634a765f52b8eec225c309549d9a1045a9b700831ab3468223de;
  wire [15:0] rdata_1005;
  SB_RAM256x16 ram_1005 (
    .RDATA(rdata_1005),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 10),
    .MASK(16'b0)
  );
defparam ram_1005.INIT_0 = 256'h0776006ec4d03f7a5c73c6057f7bbb99f7edd3d8a12be2e3861cd69aa1bc525c;
defparam ram_1005.INIT_1 = 256'hf24b4a0303bece261707dd7962cd9ab47513d64b793224f15562b4c4d72ec72c;
defparam ram_1005.INIT_2 = 256'hd30dbc4325341cdd5dcfb3d5f9410e1519c20e4b16d74676e855324ccd67af40;
defparam ram_1005.INIT_3 = 256'h4a60c84b1172429d7d8a0b7bbefc3e626e25187906cd7e14e1c316ac7e9ed288;
defparam ram_1005.INIT_4 = 256'h9d1c20f207820f24ba23a74a0da804ec13f8a1b7ed61e5a644c79e5932782489;
defparam ram_1005.INIT_5 = 256'ha2f4c117c4d10358b1b04ab329706816dce90617ee78102870d29889a7660488;
defparam ram_1005.INIT_6 = 256'h22b667287f6fed4bfee9b16292dc9c8123a2ab5dcfa8fefdfcedfe2cb1869519;
defparam ram_1005.INIT_7 = 256'hddfb1d4815eaa10a75bde6c4799ef3e1d4c0812fa1d808083bc054d21b3655f0;
defparam ram_1005.INIT_8 = 256'h6bebae5c4efe1bdf465dda9e4ca89a3a78d985462f017150b8f9d36783fc27d3;
defparam ram_1005.INIT_9 = 256'hde7dd3ae6e92319591c5d8647f2e51d38d1b0cad7683fd870d63f55fca8a1524;
defparam ram_1005.INIT_A = 256'hd27e172a81e83608bbc9ea610f3801d47a54d14a5309a4847f14abceda8fecb9;
defparam ram_1005.INIT_B = 256'ha151d1f63317c4515c9f5773a7e5812a3906738b26b9a9447ec9aceb93fe5636;
defparam ram_1005.INIT_C = 256'ha43c9e64daef57c028270e426fa141aa96209263021ae9d0c78fd98f9c148954;
defparam ram_1005.INIT_D = 256'h40d7f09924ea37080c9b7243c18c25243eeef757b2ddf45cd90f1552f2dc67f4;
defparam ram_1005.INIT_E = 256'hf09c320f602b1fa8d8321d0554a8a6613a67f43747362b7f5e2881a27d943bec;
defparam ram_1005.INIT_F = 256'h86a034c22751bb658bb02c3d653e7f3af4f1d23807a5d0850342092825c678d7;
  wire [15:0] rdata_1007;
  SB_RAM256x16 ram_1007 (
    .RDATA(rdata_1007),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 11),
    .MASK(16'b0)
  );
defparam ram_1007.INIT_0 = 256'h4e39bcdedc4225f725553e52a5ac856ffce7ec677b03371f5cfcbdc088d25d3e;
defparam ram_1007.INIT_1 = 256'h3ae63a363e292263c3767b69693f590967b4a51b7545ef66197a9e81340625f4;
defparam ram_1007.INIT_2 = 256'hd143d96571dcf7c28197a18318537b93c8fcf207cbc9c28b02e6891faa1d2060;
defparam ram_1007.INIT_3 = 256'hd4cccc72f0bc14361256a0860cf83c4036056951417bd9e9c36bb443da137a45;
defparam ram_1007.INIT_4 = 256'h19fdfb40c38ba5c327ec0e928aa904b3c82003e48245d6665ea30e6de59d95b5;
defparam ram_1007.INIT_5 = 256'h1955f4d9c2eb2e65e772a58e15b472caa748bcdfe36ff847d6b40e3144fbeec3;
defparam ram_1007.INIT_6 = 256'h1731ac85d13545f4d691a4c6b53833936ba7bf84be95a37682d3d7e8f46105ae;
defparam ram_1007.INIT_7 = 256'hff2e1b21202bc8d4e6d0924ec4f3d650c383ddecef63c838ec35fdcdbfff217a;
defparam ram_1007.INIT_8 = 256'h6cba3ae658a500c33b92d92896b897b356daf59a114db811c6386201d9933a04;
defparam ram_1007.INIT_9 = 256'hfc3a2543ec498d95e4d91a702c848c7ac8bbd9a2e427f73c9103bf231eed364f;
defparam ram_1007.INIT_A = 256'h93e1884aeb0366366c841e1f542598c2bd8b2cf31f73055007bc12d74164191b;
defparam ram_1007.INIT_B = 256'hec77a7c083657e4af9e587b26a41f9951cbc47a4998066a06fbef31e4c703a84;
defparam ram_1007.INIT_C = 256'h2fe468d39c8459102279bb9b4ee58b644a36bf6473591f8ef3cbba2a994869ba;
defparam ram_1007.INIT_D = 256'h83776c239ddd7de3a1578433608dc6a4469bf2d56f488f12b726d8ce919ea9d2;
defparam ram_1007.INIT_E = 256'h3fdc7c39c3d78e24f206100c593ae13f3504e3fdb51d0c1e0ee8deb94c2e56f8;
defparam ram_1007.INIT_F = 256'h0cf5c0b04f44cb998f2666e53fb0821fce4cd86a56cf0d9294c63badae74ea58;
  wire [15:0] rdata_1009;
  SB_RAM256x16 ram_1009 (
    .RDATA(rdata_1009),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 12),
    .MASK(16'b0)
  );
defparam ram_1009.INIT_0 = 256'h00dd22ab72977ee266ff25412fb075db016baeca9f13968d4616a585eee3090a;
defparam ram_1009.INIT_1 = 256'h13e38c740dfa42a0dd7630edf82bec6afc3e4444a24e308b45899e5c2179aa53;
defparam ram_1009.INIT_2 = 256'h46074c8da907cd884cf6a0d6c8f42c68d5aaeade7159ac472a3846993f283607;
defparam ram_1009.INIT_3 = 256'h6e9a5cdcc076f56aea6b66f2423f485b78289ed5c6192a7b88de6b149a0bcc77;
defparam ram_1009.INIT_4 = 256'hba3d1385e32eab4b82370495b8d90f5751a6dc1da47d33e82fef50b08904afa8;
defparam ram_1009.INIT_5 = 256'h070b3ab69f1e5ff13022fd403e3197f363bcf4b926a12265e8e7143b9ce57bff;
defparam ram_1009.INIT_6 = 256'h54e43106537fc4a6ee059ca2e4608f1ddf4c225a60c46b4b8c5aad9c0140e6e3;
defparam ram_1009.INIT_7 = 256'hf54a84ac1112cce38092c8ab9dc372da803fb1043313a44bc09e0ae9870882de;
defparam ram_1009.INIT_8 = 256'h7bea9c49dfce264c2887a4d75f8401384d3ecd8f4126ba767b0f559e9bc27589;
defparam ram_1009.INIT_9 = 256'hd83372f53ac2c6174a64540ebc7c0a604d6d739f6f7ec5c7c217b0f42ff28ce4;
defparam ram_1009.INIT_A = 256'h225c6c8d155ddc900609375ff62e940face07ecd4700b9a58e31f79ad4177031;
defparam ram_1009.INIT_B = 256'h6f3934aeb7cb9b817f7a1e742cd2b64c077f7b394ac65fcc5d67f2b13ef402ef;
defparam ram_1009.INIT_C = 256'h4634285a3fe505d87689ddd607abe8942354d1ff1ab96bbda0e3992cc51827f2;
defparam ram_1009.INIT_D = 256'h8f5ba84568337a4c48dd650d26e7774062012636b6be06c3d084e9e69505669d;
defparam ram_1009.INIT_E = 256'h9c8362ebbd6cdb77941d8dcc2cd9975ecf45bdab9cd5c6c6d96cd12439ba3416;
defparam ram_1009.INIT_F = 256'h6ac567c655b53b93d3dd0718c2bed6419eff6bb310b4865c1115d7d6a18dbe39;
  wire [15:0] rdata_1011;
  SB_RAM256x16 ram_1011 (
    .RDATA(rdata_1011),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 13),
    .MASK(16'b0)
  );
defparam ram_1011.INIT_0 = 256'h362c2d793cc2cbefa8f0856599ae3092fc9d1899af1176c56cf4af5204ceff43;
defparam ram_1011.INIT_1 = 256'h24a47c459b500efbdbade11495dc1563d0eb10d855e616d158903f42c85f9d7f;
defparam ram_1011.INIT_2 = 256'h22dcae4b4ea436cfcfab001745d46d018985b37ca8967cfa1acd8092b04b8f54;
defparam ram_1011.INIT_3 = 256'hafc84dc99ccba1a754e8891edcd82ef3bb3b2c3ae1cb1ec0a14f572c60d12f08;
defparam ram_1011.INIT_4 = 256'h904aa0e37fa6c8da80ef6a8494b730ce7e422c4cf13aa527573671d153cf7ce1;
defparam ram_1011.INIT_5 = 256'h03f03529f73ed23835562295897065dee7cf99f593ccef4c545193d867ac7e08;
defparam ram_1011.INIT_6 = 256'h5d2fd0e50390eccf5322efa530c77ef20d5807ae44138ca9d55c7eb221c4a3ed;
defparam ram_1011.INIT_7 = 256'h5ecf2c470973a0d8a192a9aebb1fc0634a2bc4ad471a81a56dbef77148acc224;
defparam ram_1011.INIT_8 = 256'hb729ece2b3ebf4a36f769a6fa20a6e78f448a15ae707f593097b6d2aecaa6948;
defparam ram_1011.INIT_9 = 256'h0af41c521d3c94c64b76a424110a8d95fba2b51dbf72b0b34806cb2a1088fd7e;
defparam ram_1011.INIT_A = 256'h65f51a767a25bcf8c8b922d2291a81cb43d8fd14c4f28e3f6211e685cf6bf659;
defparam ram_1011.INIT_B = 256'h525643b65c204fbc4784701c8d27bc7272d622ce3b95f6cfc3dd99df69cb3b8e;
defparam ram_1011.INIT_C = 256'ha60853f8e9d0e538e106184173fdc70b496cc3048e65f3378e0b740b76bf594f;
defparam ram_1011.INIT_D = 256'h8359c3bc1e7be748e9e74c42b2ac4ff44fa6e1a5cd485e18bf2f1674d76fc7ad;
defparam ram_1011.INIT_E = 256'h19868c5139623b8823c1f62d69ba80469415a6766cb8c4e5827ada6e7b2c107c;
defparam ram_1011.INIT_F = 256'h1c7f1dd62f29a97250327ce5d9909876004e17f1532a2d218a67980a03ded845;
  wire [15:0] rdata_1013;
  SB_RAM256x16 ram_1013 (
    .RDATA(rdata_1013),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 14),
    .MASK(16'b0)
  );
defparam ram_1013.INIT_0 = 256'h1c9b05f5062cf4c25ddeeac8024576874c7989e717a11770dca3747f29ae514a;
defparam ram_1013.INIT_1 = 256'h13cfb7cc84ef05f07fc8f83085878e6aab399c88815116dc4ad2f7c4cea680e2;
defparam ram_1013.INIT_2 = 256'h50b45abe6c1f167f5bccf97db6d7251da4321990172d4897804947f434e79b1c;
defparam ram_1013.INIT_3 = 256'hb2a152c418006c4a0e7bcc961cacaf37eedbb38830633b7fe3a124f7795f58e6;
defparam ram_1013.INIT_4 = 256'hc8b596be79c27aa527c94de1cee75f50e13465f1031d4f6e88866f2adb61806f;
defparam ram_1013.INIT_5 = 256'hcb2b6636db3b635aadfd796a226f128ff3d2005b501abee63f9caa1116367044;
defparam ram_1013.INIT_6 = 256'hfd2255e9d120bfd3df10e0dd1f3488243e58bf85058a960d9767ae3176090494;
defparam ram_1013.INIT_7 = 256'hdc0aec0de8936cc5843863a55f7d60326be11898381a27151ee3ba699a4e8d6d;
defparam ram_1013.INIT_8 = 256'h5219e84d5be7ff41723580327bf1d2931ebff70ac32a3219066af7ebe5b6d1d2;
defparam ram_1013.INIT_9 = 256'hcb5029f958e66f0e3d1b1b9df273b9131bc1d10abe226c03de9b15ff5ff9e282;
defparam ram_1013.INIT_A = 256'h02637bb03a384463fee3a500ca6b4614e19db03d8eec5214540767a13f4218d1;
defparam ram_1013.INIT_B = 256'h1d83eee108d925f34f15f03269d685d1132a5aa102f8a49ba0d216d4a2de5858;
defparam ram_1013.INIT_C = 256'h5b354f004e9a7d40dd6f4b38b9d258c6718a6db339eb23d591e96b31b4ffed14;
defparam ram_1013.INIT_D = 256'hc1c1c526ea60690e3bbf2bce2989a12e3deb4dcafc2818b37a591a15bc6fe402;
defparam ram_1013.INIT_E = 256'hc08c14e42ac9e3175d2c2ae617d71f3aac4c18ab51f4827f491bd8c7109c3db0;
defparam ram_1013.INIT_F = 256'h50929c51c7d605a973c3f518850e9ecc133cffd13a9942a69317b566dba8e78e;
  wire [15:0] rdata_1015;
  SB_RAM256x16 ram_1015 (
    .RDATA(rdata_1015),
    .RADDR(addr),
    .RCLK(clk),
    .RCLKE(1'b1),
    .RE(1'b1),
    .WADDR(addr),
    .WCLK(clk),
    .WCLKE(1'b1),
    .WDATA(wdata),
    .WE(sel == 15),
    .MASK(16'b0)
  );
defparam ram_1015.INIT_0 = 256'h12be2212ed14b2640338f81dff4108d4ac3bf1e6a03d7a29cac03cfe50e1bff8;
defparam ram_1015.INIT_1 = 256'hf485c1d5ad53c47a71709a5fb8cfcbc329f0e18b7178c13872b52c7c6a285ce4;
defparam ram_1015.INIT_2 = 256'h0f7b97d175c184936b7626f2402e106ec7a53b31b97f05b87b224270da05e334;
defparam ram_1015.INIT_3 = 256'heb2844df6eb99634216dfe81c6287f7c55d047b08034e4c32b1d824d10c64fe0;
defparam ram_1015.INIT_4 = 256'ha28fff103cf00d3a51939c8eb633d49ed059a79bb70253ef6a145fa0fba30636;
defparam ram_1015.INIT_5 = 256'he8ac62e181b16da21e581e88f0a9faf89d14e1e2e1013d7522705f7dd64d2de4;
defparam ram_1015.INIT_6 = 256'h7b90b08c103dd63a3c5423a7ee83d6a144fbf40c6fb04befa7e116b1b8a5d6b6;
defparam ram_1015.INIT_7 = 256'h6d5eae0464fff912dcde27536baa0ce0831c559a90f63df5d7dc9c2ac9cd82a2;
defparam ram_1015.INIT_8 = 256'hff802d46b492cf02aff2dc259541586414f67b86fc8c4114969f39702d29830e;
defparam ram_1015.INIT_9 = 256'h7078b25fbb5914cd4dfc3c391beb54a2c47baabae73f3ee4da1b64cf7767be72;
defparam ram_1015.INIT_A = 256'hfc517c45f85fb461e326f7a886cebeb6c977d0b285b42d1ca35042cafadee9e3;
defparam ram_1015.INIT_B = 256'h5519034f258fa5c885ea5cf8d67b379a55859ae6b38f12236e559c4b19972731;
defparam ram_1015.INIT_C = 256'hcf4251d73f1054d3986f2ac746ac44d4e0e9a0b4f179126262ffef39f4ba1756;
defparam ram_1015.INIT_D = 256'h3cd68370c54a6b68802813bb1a3181ad13166a324cf1c3eba85f8651664dde8a;
defparam ram_1015.INIT_E = 256'h8a0896ac480c525a1c702b9856da6163328b36a3ec5c2e13bc07656b71bd1575;
defparam ram_1015.INIT_F = 256'hdbccace4967a5bbacc70d66dd227a1fbd11062e04cc1cb91d6d0dcd9750fd1b7;
assign rdata = sel == 0 ? rdata_0301 : sel == 1 ? rdata_0303 : sel == 2 ? rdata_0305 : sel == 3 ? rdata_0307 : sel == 4 ? rdata_0309 : sel == 5 ? rdata_0311 : sel == 6 ? rdata_0313 : sel == 7 ? rdata_0315 : sel == 8 ? rdata_1001 : sel == 9 ? rdata_1003 : sel == 10 ? rdata_1005 : sel == 11 ? rdata_1007 : sel == 12 ? rdata_1009 : sel == 13 ? rdata_1011 : sel == 14 ? rdata_1013 : sel == 15 ? rdata_1015 : 0;
endmodule

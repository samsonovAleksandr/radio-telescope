<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.6.2">
  <drawing>
    <settings />
    <layers>
      <layer number="1" name="Top" color="1" fill="1" visible="yes" active="yes" />
      <layer number="16" name="Bottom" color="4" fill="1" visible="yes" active="yes" />
      <layer number="17" name="Pads" color="4" fill="1" visible="yes" active="yes" />
      <layer number="18" name="Vias" color="4" fill="1" visible="yes" active="yes" />
      <layer number="19" name="Unrouted" color="4" fill="1" visible="yes" active="yes" />
      <layer number="20" name="Dimension" color="4" fill="1" visible="yes" active="yes" />
      <layer number="21" name="tPlace" color="4" fill="1" visible="yes" active="yes" />
      <layer number="25" name="tNames" color="4" fill="1" visible="yes" active="yes" />
      <layer number="27" name="tValues" color="4" fill="1" visible="yes" active="yes" />
      <layer number="29" name="tStop" color="4" fill="1" visible="yes" active="yes" />
      <layer number="30" name="bStop" color="4" fill="1" visible="yes" active="yes" />
      <layer number="31" name="tCream" color="4" fill="1" visible="yes" active="yes" />
      <layer number="44" name="Drills" color="4" fill="1" visible="yes" active="yes" />
      <layer number="45" name="Holes" color="4" fill="1" visible="yes" active="yes" />
      <layer number="51" name="tDocu" color="4" fill="1" visible="yes" active="yes" />
      <layer number="91" name="Nets" color="4" fill="1" visible="yes" active="yes" />
      <layer number="92" name="Busses" color="4" fill="1" visible="yes" active="yes" />
      <layer number="93" name="Pins" color="4" fill="1" visible="yes" active="yes" />
      <layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes" />
      <layer number="95" name="Names" color="4" fill="1" visible="yes" active="yes" />
      <layer number="96" name="Values" color="4" fill="1" visible="yes" active="yes" />
    </layers>
    <schematic>
      <libraries>
        <library name="RT">
          <packages>
            <package name="CAP">
              <smd name="1" x="-0.8" y="0" dx="0.9" dy="0.95" layer="1" />
              <smd name="2" x="0.8" y="0" dx="0.9" dy="0.95" layer="1" />
              <text x="1.8" y="1.3" size="1.05" layer="25" ratio="14">&gt;NAME</text>
            </package>
            <package name="CHOKE">
              <smd name="1" x="0" y="-0.8" dx="0.95" dy="0.9" layer="1" />
              <smd name="2" x="0" y="0.8" dx="0.95" dy="0.9" layer="1" />
              <text x="-1.8" y="1.6" size="1.05" layer="25" ratio="14">&gt;NAME</text>
            </package>
            <package name="MMIC">
              <smd name="1" x="-1.5" y="-1.6" dx="0.85" dy="1.55" layer="1" />
              <smd name="2" x="0" y="-1.6" dx="0.95" dy="1.55" layer="1" />
              <smd name="3" x="1.5" y="-1.6" dx="0.85" dy="1.55" layer="1" />
              <smd name="4" x="0" y="0.65" dx="1.9" dy="2.35" layer="1" />
              <text x="-3.8" y="3.4" size="1.05" layer="25" ratio="14">&gt;NAME</text>
            </package>
            <package name="COAX">
              <smd name="1" x="0" y="0" dx="2" dy="2" layer="1" />
              <smd name="2" x="0" y="-3" dx="3" dy="2" layer="1" />
              <text x="-1" y="2" size="1.05" layer="25" ratio="14">&gt;NAME</text>
            </package>
            <package name="POWER">
              <smd name="1" x="0" y="0" dx="2" dy="2" layer="1" />
              <smd name="2" x="0" y="3" dx="2" dy="2" layer="1" />
              <text x="-4.5" y="1" size="1.05" layer="25" ratio="14">&gt;NAME</text>
            </package>
          </packages>
          <symbols>
            <symbol name="CAP">
              <wire x1="-5.08" y1="0" x2="-0.6" y2="0" layer="94" width="0.254" />
              <wire x1="-0.6" y1="-1.8" x2="-0.6" y2="1.8" layer="94" width="0.254" />
              <wire x1="0.6" y1="-1.8" x2="0.6" y2="1.8" layer="94" width="0.254" />
              <wire x1="0.6" y1="0" x2="5.08" y2="0" layer="94" width="0.254" />
              <text x="-3" y="6" size="1.5" layer="95" ratio="14">&gt;NAME</text>
              <text x="-3" y="4.25" size="1.25" layer="96" ratio="14">&gt;VALUE</text>
              <pin name="1" x="-5.08" y="0" length="point" visible="pad" direction="pas" />
              <pin name="2" x="5.08" y="0" length="point" visible="pad" direction="pas" />
            </symbol>
            <symbol name="CHOKE">
              <wire x1="0" y1="-5.08" x2="0" y2="-3" layer="94" width="0.254" />
              <wire x1="0.0" y1="-3.0" x2="0.6717514421272202" y2="-2.625" layer="94" width="0.254" />
              <wire x1="0.6717514421272202" y1="-2.625" x2="0.95" y2="-2.25" layer="94" width="0.254" />
              <wire x1="0.95" y1="-2.25" x2="0.6717514421272202" y2="-1.875" layer="94" width="0.254" />
              <wire x1="0.6717514421272202" y1="-1.875" x2="1.1634144591899854e-16" y2="-1.5" layer="94" width="0.254" />
              <wire x1="1.1634144591899854e-16" y1="-1.5" x2="-0.67175144212722" y2="-1.125" layer="94" width="0.254" />
              <wire x1="-0.67175144212722" y1="-1.125" x2="-0.95" y2="-0.75" layer="94" width="0.254" />
              <wire x1="-0.95" y1="-0.75" x2="-0.6717514421272203" y2="-0.375" layer="94" width="0.254" />
              <wire x1="-0.6717514421272203" y1="-0.375" x2="-2.326828918379971e-16" y2="0.0" layer="94" width="0.254" />
              <wire x1="-2.326828918379971e-16" y1="0.0" x2="0.6717514421272199" y2="0.375" layer="94" width="0.254" />
              <wire x1="0.6717514421272199" y1="0.375" x2="0.95" y2="0.75" layer="94" width="0.254" />
              <wire x1="0.95" y1="0.75" x2="0.6717514421272209" y2="1.125" layer="94" width="0.254" />
              <wire x1="0.6717514421272209" y1="1.125" x2="3.490243377569956e-16" y2="1.5" layer="94" width="0.254" />
              <wire x1="3.490243377569956e-16" y1="1.5" x2="-0.6717514421272205" y2="1.875" layer="94" width="0.254" />
              <wire x1="-0.6717514421272205" y1="1.875" x2="-0.95" y2="2.25" layer="94" width="0.254" />
              <wire x1="-0.95" y1="2.25" x2="-0.671751442127221" y2="2.625" layer="94" width="0.254" />
              <wire x1="-0.671751442127221" y1="2.625" x2="-4.653657836759942e-16" y2="3.0" layer="94" width="0.254" />
              <wire x1="-4.653657836759942e-16" y1="3.0" x2="0" y2="5.08" layer="94" width="0.254" />
              <text x="-3" y="6" size="1.5" layer="95" ratio="14">&gt;NAME</text>
              <text x="-3" y="4.25" size="1.25" layer="96" ratio="14">&gt;VALUE</text>
              <pin name="1" x="0" y="-5.08" length="point" visible="pad" direction="pas" />
              <pin name="2" x="0" y="5.08" length="point" visible="pad" direction="pas" />
            </symbol>
            <symbol name="MMIC">
              <wire x1="-5" y1="-4" x2="-5" y2="4" layer="94" width="0.254" />
              <wire x1="-5" y1="4" x2="5" y2="0" layer="94" width="0.254" />
              <wire x1="5" y1="0" x2="-5" y2="-4" layer="94" width="0.254" />
              <wire x1="-7.62" y1="0" x2="-5" y2="0" layer="94" width="0.254" />
              <wire x1="5" y1="0" x2="7.62" y2="0" layer="94" width="0.254" />
              <wire x1="-2.54" y1="-3" x2="-2.54" y2="-7.62" layer="94" width="0.254" />
              <wire x1="2.54" y1="-1" x2="2.54" y2="-7.62" layer="94" width="0.254" />
              <text x="-3" y="6" size="1.5" layer="95" ratio="14">&gt;NAME</text>
              <text x="-3" y="4.25" size="1.25" layer="96" ratio="14">&gt;VALUE</text>
              <pin name="1" x="-7.62" y="0" length="point" visible="pad" direction="in" />
              <pin name="3" x="7.62" y="0" length="point" visible="pad" direction="out" />
              <pin name="2" x="-2.54" y="-7.62" length="point" visible="pad" direction="pas" />
              <pin name="4" x="2.54" y="-7.62" length="point" visible="pad" direction="pas" />
            </symbol>
            <symbol name="COAX">
              <wire x1="-2" y1="-2" x2="-2" y2="2" layer="94" width="0.254" />
              <wire x1="-2" y1="2" x2="2" y2="2" layer="94" width="0.254" />
              <wire x1="2" y1="2" x2="2" y2="-2" layer="94" width="0.254" />
              <wire x1="2" y1="-2" x2="-2" y2="-2" layer="94" width="0.254" />
              <wire x1="2" y1="0" x2="5.08" y2="0" layer="94" width="0.254" />
              <wire x1="0" y1="-2" x2="0" y2="-5.08" layer="94" width="0.254" />
              <text x="-3" y="6" size="1.5" layer="95" ratio="14">&gt;NAME</text>
              <text x="-3" y="4.25" size="1.25" layer="96" ratio="14">&gt;VALUE</text>
              <pin name="1" x="5.08" y="0" length="point" visible="pad" direction="pas" />
              <pin name="2" x="0" y="-5.08" length="point" visible="pad" direction="pas" />
            </symbol>
            <symbol name="POWER">
              <wire x1="-2" y1="-2" x2="-2" y2="2" layer="94" width="0.254" />
              <wire x1="-2" y1="2" x2="2" y2="2" layer="94" width="0.254" />
              <wire x1="2" y1="2" x2="2" y2="-2" layer="94" width="0.254" />
              <wire x1="2" y1="-2" x2="-2" y2="-2" layer="94" width="0.254" />
              <wire x1="2" y1="0" x2="5.08" y2="0" layer="94" width="0.254" />
              <wire x1="0" y1="-2" x2="0" y2="-5.08" layer="94" width="0.254" />
              <text x="-3" y="6" size="1.5" layer="95" ratio="14">&gt;NAME</text>
              <text x="-3" y="4.25" size="1.25" layer="96" ratio="14">&gt;VALUE</text>
              <pin name="1" x="5.08" y="0" length="point" visible="pad" direction="pas" />
              <pin name="2" x="0" y="-5.08" length="point" visible="pad" direction="pas" />
            </symbol>
          </symbols>
          <devicesets>
            <deviceset name="CAP" uservalue="yes">
              <gates>
                <gate name="G$1" symbol="CAP" x="0" y="0" />
              </gates>
              <devices>
                <device name="" package="CAP">
                  <connects>
                    <connect gate="G$1" pin="1" pad="1" />
                    <connect gate="G$1" pin="2" pad="2" />
                  </connects>
                  <technologies>
                    <technology name="" />
                  </technologies>
                </device>
              </devices>
            </deviceset>
            <deviceset name="CHOKE" uservalue="yes">
              <gates>
                <gate name="G$1" symbol="CHOKE" x="0" y="0" />
              </gates>
              <devices>
                <device name="" package="CHOKE">
                  <connects>
                    <connect gate="G$1" pin="1" pad="1" />
                    <connect gate="G$1" pin="2" pad="2" />
                  </connects>
                  <technologies>
                    <technology name="" />
                  </technologies>
                </device>
              </devices>
            </deviceset>
            <deviceset name="MMIC" uservalue="yes">
              <gates>
                <gate name="G$1" symbol="MMIC" x="0" y="0" />
              </gates>
              <devices>
                <device name="" package="MMIC">
                  <connects>
                    <connect gate="G$1" pin="1" pad="1" />
                    <connect gate="G$1" pin="3" pad="3" />
                    <connect gate="G$1" pin="2" pad="2" />
                    <connect gate="G$1" pin="4" pad="4" />
                  </connects>
                  <technologies>
                    <technology name="" />
                  </technologies>
                </device>
              </devices>
            </deviceset>
            <deviceset name="COAX" uservalue="yes">
              <gates>
                <gate name="G$1" symbol="COAX" x="0" y="0" />
              </gates>
              <devices>
                <device name="" package="COAX">
                  <connects>
                    <connect gate="G$1" pin="1" pad="1" />
                    <connect gate="G$1" pin="2" pad="2" />
                  </connects>
                  <technologies>
                    <technology name="" />
                  </technologies>
                </device>
              </devices>
            </deviceset>
            <deviceset name="POWER" uservalue="yes">
              <gates>
                <gate name="G$1" symbol="POWER" x="0" y="0" />
              </gates>
              <devices>
                <device name="" package="POWER">
                  <connects>
                    <connect gate="G$1" pin="1" pad="1" />
                    <connect gate="G$1" pin="2" pad="2" />
                  </connects>
                  <technologies>
                    <technology name="" />
                  </technologies>
                </device>
              </devices>
            </deviceset>
          </devicesets>
        </library>
      </libraries>
      <attributes />
      <variantdefs />
      <classes>
        <class number="0" name="default" width="0" drill="0" />
      </classes>
      <parts>
        <part name="J1" library="RT" deviceset="COAX" device="" value="RF IN" />
        <part name="C1" library="RT" deviceset="CAP" device="" value="10p" />
        <part name="U1" library="RT" deviceset="MMIC" device="" value="SPF5189Z" />
        <part name="C2" library="RT" deviceset="CAP" device="" value="100p" />
        <part name="J2" library="RT" deviceset="COAX" device="" value="RF OUT" />
        <part name="L1" library="RT" deviceset="CHOKE" device="" value="47n" />
        <part name="C3" library="RT" deviceset="CAP" device="" value="100p" />
        <part name="C4" library="RT" deviceset="CAP" device="" value="100n" />
        <part name="J3" library="RT" deviceset="POWER" device="" value="5V" />
      </parts>
      <sheets>
        <sheet>
          <plain />
          <instances>
            <instance part="J1" gate="G$1" x="10.16" y="30.48" rot="R0" />
            <instance part="C1" gate="G$1" x="25.4" y="30.48" rot="R0" />
            <instance part="U1" gate="G$1" x="45.72" y="30.48" rot="R0" />
            <instance part="C2" gate="G$1" x="71.12" y="30.48" rot="R0" />
            <instance part="J2" gate="G$1" x="91.44" y="30.48" rot="MR0" />
            <instance part="L1" gate="G$1" x="58.42" y="45.72" rot="R0" />
            <instance part="C3" gate="G$1" x="78.74" y="55.88" rot="R0" />
            <instance part="C4" gate="G$1" x="78.74" y="68.58" rot="R0" />
            <instance part="J3" gate="G$1" x="30.48" y="68.58" rot="R0" />
          </instances>
          <nets>
            <net name="IN" class="0">
              <segment>
                <pinref part="J1" gate="G$1" pin="1" />
                <pinref part="C1" gate="G$1" pin="1" />
                <wire x1="15.24" y1="30.48" x2="20.32" y2="30.48" layer="91" width="0.1524" />
              </segment>
            </net>
            <net name="AMP_IN" class="0">
              <segment>
                <pinref part="C1" gate="G$1" pin="2" />
                <pinref part="U1" gate="G$1" pin="1" />
                <wire x1="30.48" y1="30.48" x2="38.1" y2="30.48" layer="91" width="0.1524" />
              </segment>
            </net>
            <net name="BIAS_RF" class="0">
              <segment>
                <pinref part="U1" gate="G$1" pin="3" />
                <pinref part="L1" gate="G$1" pin="1" />
                <pinref part="C2" gate="G$1" pin="1" />
                <wire x1="53.34" y1="30.48" x2="58.42" y2="30.48" layer="91" width="0.1524" />
                <wire x1="58.42" y1="30.48" x2="66.04" y2="30.48" layer="91" width="0.1524" />
                <wire x1="58.42" y1="30.48" x2="58.42" y2="40.64" layer="91" width="0.1524" />
                <junction x="58.42" y="30.48" />
              </segment>
            </net>
            <net name="OUT" class="0">
              <segment>
                <pinref part="C2" gate="G$1" pin="2" />
                <pinref part="J2" gate="G$1" pin="1" />
                <wire x1="76.2" y1="30.48" x2="86.36" y2="30.48" layer="91" width="0.1524" />
              </segment>
            </net>
            <net name="VCC" class="0">
              <segment>
                <pinref part="J3" gate="G$1" pin="1" />
                <pinref part="L1" gate="G$1" pin="2" />
                <pinref part="C3" gate="G$1" pin="1" />
                <pinref part="C4" gate="G$1" pin="1" />
                <wire x1="35.56" y1="68.58" x2="58.42" y2="68.58" layer="91" width="0.1524" />
                <wire x1="58.42" y1="68.58" x2="73.66" y2="68.58" layer="91" width="0.1524" />
                <wire x1="58.42" y1="68.58" x2="58.42" y2="55.88" layer="91" width="0.1524" />
                <wire x1="58.42" y1="55.88" x2="58.42" y2="50.8" layer="91" width="0.1524" />
                <wire x1="58.42" y1="55.88" x2="73.66" y2="55.88" layer="91" width="0.1524" />
                <junction x="58.42" y="68.58" />
                <junction x="58.42" y="55.88" />
              </segment>
            </net>
            <net name="GND" class="0">
              <segment>
                <pinref part="J1" gate="G$1" pin="2" />
                <wire x1="10.16" y1="25.4" x2="10.16" y2="22.86" layer="91" width="0.1524" />
                <label x="10.16" y="22.86" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="J2" gate="G$1" pin="2" />
                <wire x1="91.44" y1="25.4" x2="91.44" y2="22.86" layer="91" width="0.1524" />
                <label x="91.44" y="22.86" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="U1" gate="G$1" pin="2" />
                <wire x1="43.18" y1="22.86" x2="43.18" y2="20.32" layer="91" width="0.1524" />
                <label x="43.18" y="20.32" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="U1" gate="G$1" pin="4" />
                <wire x1="48.26" y1="22.86" x2="48.26" y2="20.32" layer="91" width="0.1524" />
                <label x="48.26" y="20.32" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="J3" gate="G$1" pin="2" />
                <wire x1="30.48" y1="63.5" x2="30.48" y2="60.96" layer="91" width="0.1524" />
                <label x="30.48" y="60.96" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="C3" gate="G$1" pin="2" />
                <wire x1="83.82" y1="55.88" x2="83.82" y2="53.34" layer="91" width="0.1524" />
                <label x="83.82" y="53.34" size="1.2" layer="95" />
              </segment>
              <segment>
                <pinref part="C4" gate="G$1" pin="2" />
                <wire x1="83.82" y1="68.58" x2="83.82" y2="66.03999999999999" layer="91" width="0.1524" />
                <label x="83.82" y="66.03999999999999" size="1.2" layer="95" />
              </segment>
            </net>
          </nets>
        </sheet>
      </sheets>
    </schematic>
  </drawing>
</eagle>
%global debug_package %{nil}

Name:             netty
Version:          4.1.13
Release:          15
Summary:          Asynchronous event-driven network application Java framework
License:          ASL 2.0
URL:              https://netty.io/
Source0:          https://github.com/netty/netty/archive/netty-%{version}.Final.tar.gz
Source1:          codegen.bash
Patch0000:        0001-Remove-OpenSSL-parts-depending-on-tcnative.patch
Patch0001:        0002-Remove-NPN.patch
Patch0002:        0003-Remove-conscrypt-ALPN.patch
Patch0003:        CVE-2019-16869.patch
Patch0004:        CVE-2019-20444.patch
Patch0005:        CVE-2019-20445-1.patch
Patch0006:        CVE-2019-20445-2.patch
Patch0007:        CVE-2019-20445-3.patch
Patch0008:        CVE-2020-11612.patch
Patch0009:        CVE-2021-21290.patch
Patch0010:        CVE-2021-21295-pre1.patch
Patch0011:        CVE-2021-21295-pre2.patch
Patch0012:        CVE-2021-21295-pre3.patch
Patch0013:        CVE-2021-21295-pre4.patch
Patch0014:        CVE-2021-21295.patch
Patch0015:        CVE-2021-21409.patch
Patch0016:        fix-build-error.patch
Patch0017:        CVE-2021-37136.patch
Patch0018:        CVE-2021-37137.patch
Patch0019:        CVE-2021-43797-pre.patch
Patch0020:        CVE-2021-43797.patch

BuildRequires:    maven-local mvn(ant-contrib:ant-contrib)
BuildRequires:    mvn(com.jcraft:jzlib) mvn(commons-logging:commons-logging)
BuildRequires:    mvn(kr.motd.maven:os-maven-plugin) mvn(log4j:log4j:1.2.17)
BuildRequires:    mvn(org.apache.felix:maven-bundle-plugin) mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:    mvn(org.apache.maven.plugins:maven-dependency-plugin) mvn(org.apache.maven.plugins:maven-remote-resources-plugin)
BuildRequires:    mvn(org.codehaus.mojo:build-helper-maven-plugin) mvn(org.codehaus.mojo:exec-maven-plugin)
BuildRequires:    mvn(org.fusesource.hawtjni:maven-hawtjni-plugin) mvn(org.javassist:javassist)
BuildRequires:    mvn(org.jctools:jctools-core) mvn(org.slf4j:slf4j-api)
BuildRequires:    mvn(org.sonatype.oss:oss-parent:pom:)
BuildRequires:    mvn(com.fasterxml:aalto-xml)
BuildRequires:    mvn(com.ning:compress-lzf)
BuildRequires:    mvn(org.apache.logging.log4j:log4j-api) mvn(org.bouncycastle:bcpkix-jdk15on)
BuildRequires:    mvn(org.jboss.marshalling:jboss-marshalling) mvn(org.eclipse.jetty.alpn:alpn-api)

%description
Netty is an asynchronous event-driven network application framework
for rapid development of maintainable high performance protocol servers & clients.
%package    help
Summary:          Documents for %{name}
Buildarch:        noarch
Requires:         man info
Provides:         %{name}-javadoc = %{version}-%{release}
Obsoletes:        %{name}-javadoc < %{version}-%{release}
%description help
Man pages and other related documents for %{name}.

%prep
%autosetup -p1 -n netty-netty-%{version}.Final

%pom_disable_module "transport-rxtx"
%pom_remove_dep ":netty-transport-rxtx" all
%pom_disable_module "transport-udt"
%pom_remove_dep ":netty-transport-udt" all
%pom_remove_dep ":netty-build" all
%pom_disable_module "example"
%pom_remove_dep ":netty-example" all
%pom_disable_module "testsuite"
%pom_disable_module "testsuite-autobahn"
%pom_disable_module "testsuite-osgi"
%pom_disable_module "tarball"
%pom_disable_module "microbench"

%pom_xpath_inject 'pom:plugin[pom:artifactId="maven-remote-resources-plugin"]' '
<dependencies>
<dependency>
<groupId>io.netty</groupId>
<artifactId>netty-dev-tools</artifactId>
<version>${project.version}</version>
</dependency>
</dependencies>'
%pom_remove_plugin :maven-antrun-plugin
%pom_remove_plugin :maven-dependency-plugin
%pom_remove_plugin :xml-maven-plugin
%pom_remove_plugin -r :maven-checkstyle-plugin
%pom_remove_plugin -r :animal-sniffer-maven-plugin
%pom_remove_plugin -r :maven-enforcer-plugin
%pom_remove_plugin -r :maven-shade-plugin
%pom_remove_plugin -r :maven-release-plugin
%pom_remove_plugin -r :maven-clean-plugin
%pom_remove_plugin -r :maven-source-plugin
%pom_remove_plugin -r :maven-deploy-plugin
%pom_remove_plugin -r :maven-jxr-plugin
%pom_remove_plugin -r :maven-javadoc-plugin
%pom_remove_plugin -r :forbiddenapis

cp %{SOURCE1} common/codegen.bash
chmod a+x common/codegen.bash
%pom_add_plugin org.codehaus.mojo:exec-maven-plugin common '
<executions>
    <execution>
        <id>generate-collections</id>
        <phase>generate-sources</phase>
        <goals>
            <goal>exec</goal>
        </goals>
        <configuration>
            <executable>common/codegen.bash</executable>
        </configuration>
    </execution>
</executions>
'
%pom_remove_plugin :groovy-maven-plugin common
%pom_remove_dep -r "com.google.protobuf:protobuf-java"
%pom_remove_dep -r "com.google.protobuf.nano:protobuf-javanano"
rm codec/src/main/java/io/netty/handler/codec/protobuf/*
sed -i '/import.*protobuf/d' codec/src/main/java/io/netty/handler/codec/DatagramPacket*.java

sed -i 's|taskdef|taskdef classpathref="maven.plugin.classpath"|' all/pom.xml

%pom_xpath_inject "pom:plugins/pom:plugin[pom:artifactId = 'maven-antrun-plugin']" '<dependencies><dependency><groupId>ant-contrib</groupId><artifactId>ant-contrib</artifactId><version>1.0b3</version></dependency></dependencies>' all/pom.xml
%pom_xpath_inject "pom:execution[pom:id = 'build-native-lib']/pom:configuration" '<verbose>true</verbose>' transport-native-epoll/pom.xml

%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-bundle-plugin']/pom:executions/pom:execution[pom:id = 'generate-manifest']/pom:configuration/pom:instructions/pom:Import-Package" common/pom.xml

%mvn_package ":::linux*:"

%mvn_package ':*-tests' __noinstall

# remove the BuildRequires lzma-java that is deprecated
%pom_remove_dep -r "com.github.jponge:lzma-java"
rm -f codec/src/main/java/io/netty/handler/codec/compression/LzmaFrameEncoder.java
rm -f codec/src/test/java/io/netty/handler/codec/compression/LzmaFrameEncoderTest.java

%pom_remove_dep -r net.jpountz.lz4:lz4
rm -f codec/src/*/java/io/netty/handler/codec/compression/Lz4*.java

%build
export CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
%mvn_build -f


%install
%mvn_install


%files -f .mfiles
%doc LICENSE.txt NOTICE.txt


%files help -f .mfiles-javadoc


%changelog
* Fri Apr 22 2022 wangkai <wangkai385@h-partners.com> - 4.1.13-15
- Remove lz4-java dependency and fix CVE-2021-43797

* Wed Oct 27 2021 wangkai <wangkai385@huawei.com> - 4.1.13-14
- fix CVE-2021-37136 CVE-2021-37137

* Mon Aug 16 2021 wangyue <wangyue92@qq.com> - 4.1.13-13
- fix build error

* Tue Apr 06 2021 wangxiao <wangxiao65@huawei.com> - 4.1.13-12
- Fix CVE-2021-21295 CVE-2021-21409

* Tue Mar 09 2021 wangyue <wangyue92@huawei.com> - 4.1.13-11
- fix CVE-2021-21290

* Thu Jan 28 2021 maminjie <maminjie1@huawei.com> - 4.1.13-10
- remove the BuildRequires lzma-java that is deprecated

* Fri Dec 04 2020 caodongxia <caodongxia@huawei.com> - 4.1.13-9
- fix CVE-2019-16869 CVE-2019-20444 CVE-2019-20445 CVE-2020-11612
 
* Wed Aug 26 2020 yaokai <yaokai13@huawei.com> - 4.1.13-8
 - Disable support for protobuf in the codecs module

* Mon Dec 23 2019 Shuaishuai Song <songshuaishuai2@huawei.com> - 4.1.13-7
- package init

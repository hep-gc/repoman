import re
import sys
import uuid
import unittest
from subprocess import Popen, PIPE, STDOUT


class RepomanCLITest(unittest.TestCase):
    """
    Base class for all Repoman CLI tests.
    """

    def setUp(self):
        # Nothing to do for now...
        pass

    def tearDown(self):
        # Nothing to do for now...
        pass

    def run_repoman_command(self, args):
        """
        This method will call the repoman application in a subprocess
        and pass it the given command line argument string.
        The output and the return code of the repoman invocation will be
        returned to the caller for further inspection.
        """
        try:
            cmd = 'repoman %s' % (args)
            print 'Running [%s]' % (cmd)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            output = p.communicate()[0]
            return (output, p.returncode)
        except Exception, e:
            print 'Error running repoman command.\n%s' % (e)
            sys.exit(-1)
            

    def get_unique_image_name(self):
        """
        Use this method to easily create a unique image name to use in 
        your tests.
        """
        return str(uuid.uuid1())




#####################################################################
#####################################################################
#####################################################################
#
# Test cases implementation go here...
#
#


#####################################################################
#		COMMAND - 'repoman about'
#####################################################################
class AboutTest(RepomanCLITest):
    def test_about(self):
	(output, returncode) = self.run_repoman_command('about')
	p = re.search(r'client version:.*\n\s*config files in use:.*\n\s*repository_host:.*\n\s*repository_port:.*\n\s*user_proxy_cert:.*\n\s*snapshot:.*\n\s*mountpoint:.*\n\s*lockfile:.*\n\s*system_excludes:.*\n\s*user_excludes:.*\n\s*logging:', output)
	self.assertEqual(returncode, 0)
	self.assertTrue( p != None)

######################################################################
#		COMMAND - 'repoman version'
######################################################################
class ClientVersionTest(RepomanCLITest):
    def test_version(self):
        (output, returncode) = self.run_repoman_command('version')
        self.assertEqual(output, '0.3.11\n')
        self.assertEqual(returncode, 0)

######################################################################
#		COMMAND - 'repoman whoami'
######################################################################

class WhoamiTest(RepomanCLITest):
    def test_whoami(self):
        (output, returncode) = self.run_repoman_command('whoami')
        self.assertEqual(returncode, 0)

######################################################################

def CheckOptions(self, output, arg): 			
	"""
	CheckOptions method tests the common optional parameters for create-image and modify-image
	"""

	# If unauthenticated access is set as true or false while creating or modifying an image,
	# the status is checked in the output of 'repoman list-images' using regular expression 	
	if(arg == "--unauthenticated_access true" or arg == "-a true"):
		p = re.search('^\\s*unauthenticated_access : True\\s*$', output,flags=re.MULTILINE)
		self.assertTrue(p != None) 
	elif (arg == '--unauthenticated_access false' or arg == '-a false'):
                p = re.search('^\\s*unauthenticated_access : False\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If a description is given as "Random discription" while creating or modifying an image, 
	# the corresponding description is checked in the output of 'repoman list-images'
	elif (arg == '--description "Random description"' or arg == '--d "Random description"'):
		p = re.search('^\\s*description : Random description\\s*$', output, flags=re.MULTILINE)
		self.assertTrue(p != None)
	
	# If the hypervisor is set to or changed to a particular value (here 'xen'), it is checked in the output
	# of 'repoman list-images'
	elif (arg =='--hypervisor xen' or arg == '-h "xen"'):
		p = re.search('^\\s*hypervisor : xen\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If the Operating System Architecture is set to or changed to a particular value (here 'x86'),
	# the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_arch x86'):
                p = re.search('^\\s*os_arch : x86\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System type is set to or changed to a particular value (here 'linux'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_type linux'):
                p = re.search('^\\s*os_type : linux\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System Variant is set to or changed to a particular value (here 'ubuntu'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_variant ubuntu'):
                p = re.search('^\\s*os_variant : ubuntu\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)


######################################################################
#		COMMAND - 'repoman create-image'		     	
######################################################################



class CreateImageTest(RepomanCLITest):
    new_image_name = None
	
    def CreateImage(self, arg):
	"""
    	CreateImage method is called whenever the create-image command is used (with or without optional parameters)
    	Optional parameters are stored in arg. 
    	When create-image is called without options, arg is passed as an empty string
    	"""
        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()
	
        # Now let's run the 'repoman create-image' command and check it's
        # output and exit code.
        (output, returncode) = self.run_repoman_command('create-image %s %s' % (self.new_image_name, arg))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)

        # Here we actually do a 'repoman list-image' to see if the image is
        # actually there.  We use a regular expression to inspect the output.
        (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name), 
                      output, 
                      flags=re.MULTILINE)
        self.assertTrue(m != None)        
	
	CheckOptions(self, output, arg)


    def tearDown(self):
        # Delete the image we created to clean up properly after the test.
       	(output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))

   
    def test_create_image(self):
	CreateImageTest.CreateImage(self,'')

    
    # Test the alias of create-image command ('repoman ci')	
    def test_ci(self):	
	self.new_image_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('ci %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name),
                      output,
                      flags=re.MULTILINE)
        self.assertTrue(m != None)


	#########################################################
	#		OPTIONAL PARAMETERS			#	
	#########################################################

    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # Each case is in individual tests to ensure teardown (removing image after creating one)
    def test_create_image_unauthenticated_access_true(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access true')
    def test_create_image_a_true(self):		
	CreateImageTest.CreateImage(self,'-a true')
    def test_create_image_unauthenticated_access_false(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access false')       
    def test_create_image_a_false(self):   
	CreateImageTest.CreateImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_create_image_description(self):
	CreateImageTest.CreateImage(self, '--description "Random description"')
    def test_create_image_d(self):
        CreateImageTest.CreateImage(self, '--d "Random description"')
 
	
    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_create_image_hypervisor(self):
	CreateImageTest.CreateImage(self, '--hypervisor xen')
    def test_create_image_h(self):
	CreateImageTest.CreateImage(self, '-h "xen"') 
	
    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_create_image_os_arch(self):
	CreateImageTest.CreateImage(self, '--os_arch x86')	

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_create_image_os_type(self):
        CreateImageTest.CreateImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_create_image_os_variant(self):
        CreateImageTest.CreateImage(self, '--os_variant ubuntu')

    def CreateImageFile(self, arg):
	"""
	CreateImageFile method tests the optional parameters '--file' or '-f', which creates an image by uploading a file
	It tests the optional parameter passed to arg. arg can be '--file' or '-f'
	"""
	# Get a unique name for the image and a dummy file that will be uploaded
	self.new_image_name = self.get_unique_image_name()
	random_file = self.get_unique_image_name()
	# Create a dummy file of 10 MB(10485760 bytes) with a unique name
	p = Popen('dd if=/dev/zero of=%s bs=10485760 count=1' % (random_file), shell=True, stdout=PIPE, stderr=STDOUT)
	output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)
	
        # Try optional commands '--file' or '-f' with the unique name generated above as the name of the image
	(output, returncode) = self.run_repoman_command('create-image %s %s %s' % (self.new_image_name, arg, random_file))
	p = re.search(r'.+OK.+ Created new image.+\nUploading %s to new image.+\n.+OK.+%s uploaded to image.+' % (random_file, random_file), output)       
	self.assertTrue(p != None)
        self.assertEqual(returncode, 0)

        # Here we actually do a 'repoman list-image' to see if the image is
        # actually there.  We use a regular expression to inspect the output.
        (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name), output, flags=re.MULTILINE)
        self.assertTrue(m != None)
	
	# Change the unauthenticated access to true so that the file can be downloaded
	(output, returncode) = self.run_repoman_command('modify-image %s --unauthenticated_access true' % (self.new_image_name))
	self.assertEqual(returncode, 0)

	# Retrieve the url of the file and and download it using wget
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	m = re.findall(r'http://.+', output)
	p = Popen('wget %s' % (m[0]), shell=True, stdout=PIPE, stderr=STDOUT)
 	output = p.communicate()[0]
        self.assertEqual(p.returncode, 0)
	
	# Check if that file got uploaded and consequently downloaded matches the original file
	p = Popen('diff %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)
	
	# Delete the dummy file (random_file) and the downloaded file
	p = Popen('rm %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)


    def test_create_image_file(self):
	CreateImageTest.CreateImageFile(self, '--file')

    def test_create_image_f(self):
	CreateImageTest.CreateImageFile(self, '-f')

		
######################################################################
#               COMMAND - 'repoman modify-image'                        
######################################################################

class ModifyImageTest(RepomanCLITest):
    new_image_name = None
    	
    def ModifyImage(self, arg):
	"""
    	ModifyImage function is called whenever the modify-image command is used (with or without optional parameters)
    	Optional parameters are stored in arg. 
    	When modify-image is called without options, arg is passed as an empty string
	"""


        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()

        # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	
	# 'random_name' variable stores the new name for an image when '-n' or '--new_name' parameters are used
	# It is used to prevent removal of the image with the original name (which wouldn't exist after the name is changed,
	# in the tearDown method. The default is set to None
	global random_name
	random_name = None
	if (arg == '--new_name ' or arg == '-n '):
		
		random_name = self.get_unique_image_name()
		arg = arg + random_name	
	# Run 'repoman modify-image' and check the output
	(output, returncode) = self.run_repoman_command('modify-image %s %s' %(self.new_image_name, arg))
	self.assertEqual(output, "[OK]     Modifying image.\n")
	self.assertEqual(returncode, 0)
	
	if (arg == '--new_name %s' % (random_name) or arg == '-n %s' % (random_name)):
		(output, returncode) = self.run_repoman_command('list-images %s' % (random_name))
		p = re.search('^\\s*name : %s\\s*$' % (random_name), output, flags=re.MULTILINE)
                self.assertTrue(p != None)
		
		
		
	# Call CheckOptions to check some common optional parameters of create-image and modify-image
	if(random_name == None):
		(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
		CheckOptions(self, output, arg)
	
	
	
    def tearDown(self):
	if (random_name != None):
		(output, returncode) = self.run_repoman_command('remove-image -f %s' % (random_name))
	else:
		# Delete the image we created to clean up properly after the test.
        	(output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))
		
    def test_modify_image(self):
	ModifyImageTest.ModifyImage(self, '')
    
    # Test the alias of modify-image ('repoman mi')		
    def test_mi(self):
	global random_name
	random_name  = None
	self.new_image_name = self.get_unique_image_name()
	 # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
        # Run 'repoman modify-image' and check the output
        (output, returncode) = self.run_repoman_command('mi %s' %(self.new_image_name))
        self.assertEqual(output, "[OK]     Modifying image.\n")
        self.assertEqual(returncode, 0)	


        #########################################################
        #               OPTIONAL PARAMETERS                     #       
        #########################################################

    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # Each case is in individual tests to ensure teardown (removing image after creating one)
    def test_modify_image_unauthenticated_access_true(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access true')
    def test_modify_image_a_true(self):
        ModifyImageTest.ModifyImage(self,'-a true')
    def test_modify_image_unauthenticated_access_false(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access false')
    def test_modify_image_a_false(self):
        ModifyImageTest.ModifyImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_modify_image_description(self):
        ModifyImageTest.ModifyImage(self, '--description "Random description"')
    def test_modify_image_d(self):
        ModifyImageTest.ModifyImage(self, '--d "Random description"')


    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_modify_image_hypervisor(self):
        ModifyImageTest.ModifyImage(self, '--hypervisor xen')
    def test_modify_image_h(self):
        ModifyImageTest.ModifyImage(self, '-h "xen"')

    
    # Test the optional parameter '--new_name' or '-n'
    # A random name is kept as the new name which is generated later in the method ModifyImage
    def test_modify_image_new_name(self, tearDown = None):
	ModifyImageTest.ModifyImage(self, '--new_name ')
    def test_modify_image_n(self):
	ModifyImageTest.ModifyImage(self, '-n ')		

    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_modify_image_os_arch(self):
        ModifyImageTest.ModifyImage(self, '--os_arch x86')

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_modify_image_os_type(self):
        ModifyImageTest.ModifyImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_modify_image_os_variant(self):
        ModifyImageTest.ModifyImage(self, '--os_variant ubuntu')

    




#####################################################################
# 		COMMAND - 'repoman list-images'
#####################################################################

class ListImagesTest(RepomanCLITest):

    new_image_name = None
    def ListImages(self, command):
	"""
	The method ListImages is used for the commands 'repoman list-images' and 'repoman li' without optional parameters
	"""
	self.new_image_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
	self.assertEqual(returncode, 0)
	if (command == 'list-images'):
		(output, returncode) = self.run_repoman_command("list-images")
	elif (command == 'li'):
		(output, returncode) = self.run_repoman_command("li")
	p = re.search(self.new_image_name, output)
	self.assertTrue( p != None)
	self.assertEqual(returncode, 0)
	
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-image -f %s' %(self.new_image_name))

    def test_list_images(self):
	ListImagesTest.ListImages(self, 'list-images')	

    def test_li(self):
	ListImagesTest.ListImages(self, 'list-images')
    
    def test_list_images_image(self):
	"""
	This test runs the 'repoman list-images image' command, and checks if all the fields of the output match the expected fields of the image
	"""
	self.new_image_name = self.get_unique_image_name()
        (output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	(output, returncode) = self.run_repoman_command("list-images %s" % (self.new_image_name))
	p = re.search(r'checksum :.*\n\s*description :.*\n\s*expires :.*\n\s*file_url :.*\n\s*http_file_url :.*\n\s*hypervisor :.*\n\s*modified :.*\n\s*name : %s.*\n\s*os_arch :.*\n\s*os_type :.*\n\s*os_variant :.*\n\s*owner :.*\n\s*owner_user_name :.*\n\s*raw_file_uploaded :.*\n\s*read_only :.*\n\s*shared_with :.*\n\s*size :.*\n\s*unauthenticated_access :.*\n\s*uploaded :.*\n\s*uuid :.*\n\s*version :' % (self.new_image_name), output)
	self.assertTrue( p != None)
        self.assertEqual(returncode, 0)
	
#####################################################################
#####################################################################
#####################################################################




#
# The entrypoint into the script.
# No need to modify this at this point.
#

if __name__ == '__main__':
    unittest.main()

